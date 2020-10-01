from coursebuilder.parse_schedule import parse
from coursebuilding.create_bibliography import main as create_bib
import sys


command = sys.argv[1]

if command == "create_bibliography":
    create_bib()
elif command = "parse_schedule":
    parse()
