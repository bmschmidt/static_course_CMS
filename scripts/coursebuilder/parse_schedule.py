import yaml
import arrow
import re
import sys
from .settings import dir, course_settings
from typing import Dict, Tuple, Sequence, Union, List, Iterable, Optional
from arrow.arrow import Arrow

week = 1
citation_regex = r"([^\[ /]*_[^\[ /]*_[0-9]{4}[a-g]?)"
date_format = "ddd, MMM DD"
iso_format = "YYYY-MM-DD"

def load(x):
    return yaml.load(open(x), Loader = yaml.SafeLoader)

day_codes = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6
}
def format_assignments(session: dict, date: Arrow) -> List[Tuple[Arrow, str]]:
    try:
        assignments = session['assignments']
    except KeyError:
        try:
            assignments = [session['assignment']]
        except KeyError:
            return []
    val : List[Tuple[Arrow, str]] = []
    for assignment in assignments:
        if isinstance(assignment, str):
            assignment = {
                "text": assignment,
                "due": "today"
            }
        elif isinstance(assignment, dict):
            if not "due" in assignment:
                raise NameError("Must include 'due' in assignment.")
            if not "text" in assignment:
                raise NameError("Must include 'text' in assignment")
        else:
            raise TypeError("assignments must be strings or dicts")
        val.append(format_assignment(assignment, date))
    return val
        
def format_assignment(assignment : Dict[str, str], date : Arrow) -> Tuple[Arrow, str]:
    due : str = assignment['due']
    text : str = assignment['text'] 
    try:
        due = arrow.get('due')
    except:
        duedate = date
        if due.startswith("next "):
            due = due.strip("next ")
            duedate = duedate.shift(days=7)
        elif due.startswith("this "):
            due = due.strip("this ") # Meaningless.
        if due in day_codes:
            duedate.shift(weekday = day_codes[due])
        elif due.startswith("today"):
            pass
        else:
            try: 
                due = arrow.get("2020/" + due)
            except:                
                raise NameError(f"Unable to parse date {due}")
        due = duedate
    text = f"**Due {due.format(date_format)}:** {text}\n\n" 
    return (due, text)
    
def format_session(session = None, date = None, seminar = False):
    global week
    text = []
    if 'unit' in session:
        text.append(f"## {session['unit']}")
    if date is not None and 'title' in session and session['title']:
        text.append(f"### {date.format(date_format)} \n\n {session['title']}")
        if seminar:
            week += 1
            text.append(f"### Week {week} ({date}) \n\n {session['title']}")
            
    elif 'date' in session:
        text.append(f"### {session['date']}")
        
    for k, v in session.items():
        if k in ['unit', 'date', 'title', 'notes', 'assignment', 'assignments']:
            # Handled elsewhere:
            continue
        else:
            text.append(markdown_of_list_or_str(k, v))
    return "\n\n".join(text) + "\n\n\n"


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
            val = re.sub(citation_regex, "@\\1", val)
            output.append(f"* {val}")
    else:
        output.append(f"{k}: {v}")
    return "\n".join(output)


class Meetings(object):
    def __init__(self, meta, days):
        try:
            self.c = load("calendars.yml")[meta['calendar']]
        except KeyError:
            raise KeyError("Your course.yml file must define a calendar in calendars.yml")
        breaks : Dict[Arrow, str] = dict()
        for bb in self.c['breaks']:
            d = arrow.get(bb['start'])
            breaks[d] = bb['name']
            if 'end' in bb:
                while d < arrow.get(bb['end']):
                    d = d.shift(days = 1)
                    breaks[d] = bb['name']
        self.breaks = breaks
        self.reschedule_from : Dict[Arrow, Arrow] = {}
        self.reschedule_to : Dict[Arrow, Arrow] = {}
        self.reschedule_reason: Dict[Arrow, String] = {}
        print(self.c['reschedules'])
        for v in self.c['reschedules']:
            name = v['name']
            from_ = arrow.get(v['from'])
            to_ = arrow.get(v['to'])
            self.reschedule_from[to_] = from_
            self.reschedule_to[from_] = to_
            self.reschedule_reason[from_] = v['name']
        # Make iteration easier.
        self.day = arrow.get(self.c['start_date']).shift(days = -1)
        self.end = arrow.get(self.c['end_date'])        
        self.days = days
        
    def __iter__(self) -> Iterable[Tuple[Arrow, str]]:
        days = self.days
        while True:
            self.day = self.day.shift(days = 1)            
            if self.day > self.end:
                break
            if not self.day.format("ddd") in days:
                continue
            message = ""
            date : Arrow = self.day
            if date in self.breaks:
                message = f"No class: {self.breaks[date]}"
                
            if date in self.reschedule_from:
                new_date : Arrow = self.reschedule_to[date]
                message = new_date.format(date_format)
                reason : str = self.reschedule_reason[date]
                message += f" (rescheduled--{reason})"
                date = arrow.get(new_date)
            yield (date, message)


def parse():
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
        

    import os
    extant_lectures = os.listdir(f"{dir}/Lectures")
    meeting_dates = [j for j in meetings]
    all_sessions = [s for s in sessions]
    
    items : List[Tuple[Arrow, str]] = []
    
    last_date : Arrow = meetings.day
    
    while True:
        try:
            current_session = all_sessions.pop(0)
        except IndexError:
            # Missing info for session.
            while len(meeting_dates) > 0:
                (arrow_date, date_message) = meeting_dates.pop(0)
                items.append((arrow_date, f"""### {arrow_date.format(date_format)}\n\nTBD\n\n"""))
            break
            
        # Now we have a current_session.
        
        if not 'title' in current_session:
            if 'preamble' in current_session:
                items.append((arrow.get("1900-01-01"), current_session['preamble'] + "\n\n"))
            else:
                raise TypeError("HUH??")
            continue
        # Grab the date
        try:
            (arrowdate, date_message) = meeting_dates.pop(0)
        except IndexError:
            arrowdate, date_message = arrow.get("1980-09-18"), None
        # Send the date to the lectures folder.
        while date_message != "":
            items.append((arrowdate, f"""### {arrowdate.format(date_format)}\n\n{date_message}\n\n"""))
            (arrowdate, date_message) = meeting_dates.pop(0)
           
        title = current_session['title']
        session_info[title] = {'date': arrowdate}
        space_title = title.replace(" ", "_")
        if space_title + ".md" in extant_lectures:
            with open(f"{dir}/Lectures/" + space_title + ".yml", "w") as t:
                t.write("\n---\n")
                t.write(yaml.dump({
                    'title': title,
                    'date': date.format(iso_format)
                }))
                t.write("\n...\n\n")
        items.append((arrowdate, format_session(current_session, arrowdate)))
        val : Tuple[Arrow, str]
        for val in format_assignments(current_session, arrowdate):
            items.append(val)
    schedule.write("# Schedule\n\n")
    items.sort()    
    for date, item in items:
        schedule.write(item)
