#! /usr/bin/python
import re
import glob
from .settings import dir, bibliography
from pathlib import Path

# Bibliography entries to retrieve
markdowns = dir.glob("**/*.md")
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

matchlist = [m for m in matches]

matchlist.sort()

with open(dir / ".pathkeys", "w") as fout: 
    for match in matchlist:
        fout.write(match + "\n")
