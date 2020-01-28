import yaml
from pathlib import Path

dir = Path("course")

course_settings = yaml.load(open(f"{dir}/course.yml"), yaml.SafeLoader)
bibliography = Path("~/Dropbox/MyLibrary.bib").expanduser()

def get_course():
    #write_safe
    return yaml.load(open(f"{dir}/course.yml"), yaml.SafeLoader)
