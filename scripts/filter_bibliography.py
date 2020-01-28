#! /usr/bin/python
import re
import glob
from settings import dir, bibliography
from pathlib import Path

# Bibliography entries to retrieve
markdowns = dir.glob("**/*.md")
output = Path(f"{dir}/works_cited.bib").expanduser().open("w")

matches = set([])

for file in markdowns:
    for line in open(file):
        citations = re.search(r"@([A-Za-z0-9_][A-Za-z0-9_:\.#$%&\-\+\?<>~]+[A-Za-z0-9_])",line)
        if citations:
            for match in citations.groups():
                # This also matches emails.
                if match.endswith(".edu"):
                    continue
                if match.endswith(".com"):
                    continue                
                matches.add(match)

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
                output.write(line)
                # End of an entry -- should be the one which began earlier
                keep_printing = False

        if keep_printing:
            # The intermediate lines
            output.write(line)


print("Missing keys:")

for m in matches:
    print("*" + m)
