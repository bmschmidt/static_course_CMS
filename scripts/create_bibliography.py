#! /usr/bin/python
import re
import glob
from settings import dir, bibliography
from pathlib import Path

matches = set([line.rstrip() for line in open(f"{dir}/.pathkeys")])

with (dir / "works_cited.bib").open("w") as output:
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

