from coursebuilder.parse_schedule import parse
from coursebuilder.create_bibliography import main as create_bib
import sys


command = sys.argv[1]

if command == "create_bibliography":
    sys.argv.pop(0)
    create_bib()
elif command == "parse_schedule":
    sys.argv.pop(0)
    parse()
