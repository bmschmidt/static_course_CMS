import yaml
import arrow
import re
from settings import dir, course_settings

schedule = f"{dir}/syllabus/schedule.yml"

def load(x):
    return yaml.load(open(x), Loader = yaml.SafeLoader)

for line in open(schedule):
    if "- @" in line:
        print(line)
        raise yaml.scanner.ScannerError("This line ain't gonna work")
        
def format_session(session, date):
    global unit_number
    text = []
    if 'unit' in session:
        text.append(f"## {session['unit']}")
    if 'date' in session:
        raise TypeError("Haven't figured this out yet")
    text.append(f"### {date} \n\n {session['title']}")

    for k, v in session.items():
        if k in ['unit', 'date', 'title', 'notes']:
            # Handled elsewhere:
            continue
        else:
            text.append(markdown_of_list_or_str(k, v))
    return "\n\n".join(text) + "\n\n\n"

citation_regex = r"([^\[ ]*_[^\[ ]*_[0-9]*[a-g]?)"

def markdown_of_list_or_str(k, v):
    output = []
    
    if isinstance(v, list):
        output.append(f"""\n{k.capitalize()}\n""")

        for val in v:
            if val is None:
                continue
            # Crazy, but fine for personal use. If you put in a Zotero citation 
            if isinstance(val, list) and re.search(citation_regex, val[0]):
                val = ", ".join(val)
            print(val)
            val = re.sub(citation_regex, "@\\1", val)
            output.append(f"* {val}")
    else:
        print(v)
        output.append(f"{k}: {v}")
    return "\n".join(output)

sessions = load(schedule)
meta = course_settings
days = meta['days']
date_format = "ddd, MMM DD"
iso_format = "YYYY-MM-DD"

class Meetings(object):
    def __init__(self, meta):
        self.c = load("../calendars.yml")[meta['calendar']]
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

    def __iter__(self):
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

meetings = Meetings(meta)
session_info = {}

schedule = open(f"{dir}/syllabus/Schedule.md", "w")
schedule.write("# Schedule\n\n")

import os
extant_lectures = os.listdir(f"{dir}/Lectures")

for date, isodate, message in meetings:
    session_info
    if message is not None:
        output = f"""### {date}\n\n{message}\n\n"""
    if message is None:
        try:
            sess = sessions.pop(0)
            title = sess['title']
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
            else:
                print(space_title)
            output = format_session(sess, date)
        except IndexError:
            output = f"""### {date}\n\nTBD/Flex\n\n"""
    schedule.write(output)

