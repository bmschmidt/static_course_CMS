#! /usr/bin/python

import re
import glob
from pathlib import Path
try:
    from settings import dir, bibliography
except:
    bibliography = Path("~/Dropbox/MyLibrary.bib").expanduser()
    dir = "."
import sys

def find_all_citekeys(dir):
    fs = Path(".").glob("**/*md")
    for f in fs:
        if not f.exists():
            # Symlinks
            continue
        text = f.open().read()
        matches = re.findall(r'\@([A-Za-z0-9_][A-Za-z0-9_:\.#$%&\-\+\?<>~]+[0-9]+[a-z]*)', text)
        if matches:
            for match in matches:
                yield match

buffer = ""
                
matches = set([l for l in find_all_citekeys(dir)])
output = Path(sys.argv[1])
    
with open(bibliography, 'r') as bib_file:
    keep_printing = False
    for line in bib_file:
        is_key = re.search(r"^@\w+\{(.*),",line)
        if is_key:
            key=is_key.groups()[0]
            if key in matches:
                keep_printing = True
                matches.remove(key)

        if line.strip() == '}':
            if keep_printing:
                buffer += line + "\n"
                # End of an entry -- should be the one which began earlier
                keep_printing = False

        if keep_printing:
            # The intermediate lines
            buffer += line


if output.exists():
    current_text = output.open().read()
    if len(current_text) == len(buffer):
        # If the bib shrinks, no need to rewrite.
        # This may require some manual rewrites, but whatever.
        sys.exit(0)
    elif len(current_text) >= len(buffer):
        # If the bib shrinks, no need to rewrite.
        # This may require some manual rewrites, but whatever.
        sys.stderr.write("The current bibliography is larger than the"
                             "one to be created: not overwriting"
                             f"Remove {bibliography} to trigger a rebuild.")
        sys.exit(0)

with output.open(mode = "w") as fout:
    fout.write(buffer)
    
#print("Missing keys:")
#for m in matches:
#    print("*" + m)

