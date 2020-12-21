import md_tools
import os
import re
import yaml
import dateutil
import dateutil.parser
import datetime
import build_site_components
import pypandoc

course = yaml.load(open("course.yml"))

lectures = build_site_components.build_lectures(just_list=True)

for lecture in lectures:
    print("")
    print("## {}: {}".format(lecture[0],lecture[1]))
    print("")
    outline = pypandoc.convert_file(lecture[2].fn,"markdown",extra_args=["--filter=/usr/local/bin/lectureToOutline","--filter=scripts/compactify"])
    print(outline.encode("utf-8"))
