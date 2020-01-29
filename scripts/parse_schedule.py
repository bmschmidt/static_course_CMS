import yaml
import arrow
import re
from settings import dir, course_settings

def load(x):
    return yaml.load(open(x), Loader = yaml.SafeLoader)

week = 1        
def format_session(session = None, date = None, seminar = False):
    global week
    text = []
    if 'unit' in session:
        text.append(f"## {session['unit']}")
    if date is not None:
        text.append(f"### {date} \n\n {session['title']}")
        if seminar:
            text.append(f"### Week {week} ({date}) \n\n {session['title']}")        
    elif 'date' in session:
        text.append(f"### {session['date']}")
        
    for k, v in session.items():
        if k in ['unit', 'date', 'title', 'notes']:
            # Handled elsewhere:
            continue
        else:
            text.append(markdown_of_list_or_str(k, v))
    week += 1
    return "\n\n".join(text) + "\n\n\n"


def markdown_of_list_or_str(k, v):
    output = []
    
    if isinstance(v, list):
        output.append(f"""\n{k.capitalize()}\n""")

        for val in v:
            if val is None:
                continue
            try:
                val = re.sub("([^ ]*_[^ ]*_[0-9]*[a-g]?)", "@\\1", val)
            except:
                raise
            output.append(f"* {val}")
    else:
        output.append(f"{k}: {v}")
    return "\n".join(output)

date_format = "ddd, MMM DD"
iso_format = "YYYY-MM-DD"

class Meetings(object):
    def __init__(self, meta, days):
        try:
            self.c = load("calendars.yml")[meta['calendar']]
        except KeyError:
            raise KeyError("Your course.yml file must define a calendar in calendars.yml")
        breaks = dict()
        for bb in self.c['breaks']:
            d = arrow.get(bb['start'])
            breaks[d.format(date_format)] = bb['name']
            if 'end' in bb:
                while d < arrow.get(bb['end']):
                    d = d.shift(days = 1)
                    breaks[d.format(date_format)] = bb['name']
        self.breaks = breaks
        # Make iteration easier.
        self.day = arrow.get(self.c['start_date']).shift(days = -1)
        self.end = arrow.get(self.c['end_date'])        
        self.days = days
        
    def __iter__(self):
        days = self.days
        while True:
            self.day = self.day.shift(days = 1)            
            if self.day > self.end:
                break
            if not self.day.format("ddd") in days:
                continue
            message = None
            repr = self.day.format(date_format)
            iso = self.day.format(iso_format)
            if repr in self.breaks:
                message = f"No class: {self.breaks[repr]}"
            yield (repr, iso, message)

import sys

def main():
    try:
        schedule, md_file = sys.argv[1:]
    except ValueError:
        schedule = sys.argv[1]
        md_file = None
    for line in open(schedule):
        if "- @" in line:
            sys.stderror.write(line)
            raise yaml.scanner.ScannerError("This line ain't gonna work")
    
    sessions = load(schedule)
    days = course_settings['days']

    meetings = Meetings(course_settings, days)
    session_info = {}

    if md_file is not None:
        schedule = open(md_file, "w")
    else:
        schedule = sys.stdout
        
    schedule.write("# Schedule\n\n")

    import os
    extant_lectures = os.listdir(f"{dir}/Lectures")
    meeting_dates = [j for j in meetings]
    all_sessions = [s for s in sessions]
    
    while True:
        try:
            current_session = all_sessions.pop(0)
        except IndexError:
            if len(meeting_dates) > 0:
                while True:
                    try:                        
                        (date, isodate, date_message) = meeting_dates.pop(0)
                        schedule.write(f"""### {date}\n\nTBD\n\n""")
                    except IndexError:
                        break
            break

        if not 'title' in current_session:
            schedule.write(format_session(current_session, None, seminar = len(days)==1))            
        else:
            # Grab the date
            (date, isodate, date_message) = meeting_dates.pop(0)
            # Send the date to the lectures folder.
            while date_message is not None:
                schedule.write(f"""### {date}\n\n{date_message}\n\n""")
                (date, isodate, date_message) = meeting_dates.pop(0)
               
            title = current_session['title']
            session_info[title] = {'date': isodate}
            space_title = title.replace(" ", "_")
            if space_title + ".md" in extant_lectures:
                with open(f"{dir}/Lectures/" + space_title + ".yml", "w") as t:
                    t.write("\n---\n")
                    t.write(yaml.dump({
                        'title': title,
                        'date': isodate
                    }))
                    t.write("\n...\n\n")
            schedule.write(format_session(current_session, date))
            
if __name__=="__main__":
    main()
