#!/usr/bin/env/python

import yaml
import sys
import os
import datetime
import dateutil
from settings import course_settings, dir
from pathlib import Path

def course_meta():
    pass

syllabus_order = [line.rstrip() for line in open(f"{dir}/syllabus/order.yml")]

class MarkdownFile(object):
    def __init__(self, fin):
        self.fin = fin
        self.fn = str(Path(fin.parent.name, fin.name))
        self.lines = [l.replace("\r", "").strip("\xef\xbb\xbf") for l in self.fin.open()]
        self.meta = {}
        self.build_doc_metadata()
        
    def extract_yaml_header_to_meta(self):
        lines = self.lines
        # Pull the yaml header out of a Markdown markdown document.
        if len(lines)==0:
            print("\n\nWARNING: EMPTY FILE AT {} BREAKING BUILD\n\n".format(self.fn))
            raise IOError("Build broken")
        if lines[0] == "---\n":
            meta_block_end = len(lines)
            for ender in ["...\n","---\n"]:
                try:
                    meta_block_end = min([meta_block_end,1+lines[1:].index(ender)])
                except ValueError:
                    continue
            new_meta = yaml.load("".join(lines[1:meta_block_end]), yaml.SafeLoader)
            self.lines = lines[(meta_block_end+1):]
        else:
            new_meta = {}

        # Strip the title in pandoc format.
        # Not bothering with author_date stuff for now.

        if self.lines[0].startswith("%"):
            new_meta["title"] = self.lines[0][1:].strip()
            self.lines = self.lines[1:]
        
        self.meta.update(new_meta)

    def title(self):
        return self.meta["title"]

    def hidden(self, future = 1, past = 180):
        try:
            ddate = self.meta["online_date"]
        except KeyError:
            ddate = self.meta["date"]
        try:
            days_in_future = (ddate - datetime.date.today()).days
        except:
            print("Badly formatted date on {}".format(self.fn))
            raise
        if days_in_future > future or days_in_future < -past:
            # Don't link to documents from last year, or next week.
            return True
        return False
    
    def needs_html_toc(self):
        headers = 0
        for i, line in enumerate(self.lines):
            if line.startswith("#"):
                headers += 1
        if headers > 4 and i > 20:
            # Lotsa headers and short.
            return "true"
        if headers >= 2 and i > 200:
            # Long text and multiple headers.
            return "true"
        return "false"

    def infer_data_from_global_yaml(self):
        doc_meta = course_settings
        # Used by RMarkdown.
        doc_meta["title"] = "" #
        self.meta.update(doc_meta)

    def infer_data_from_local_yaml(self):
        if self.fn == "syllabus/syllabus.md":
            self.meta['title'] = "Full Syllabus"
            self.meta['date'] = datetime.date(2019, 12, 1)
            return
        if self.fn == "syllabus/Schedule.md":
            self.meta['title'] = "Schedule"
            return
        try:
            yml_path = Path(self.fin.parent, self.fin.stem + ".yml")
            local_meta = yaml.load(yml_path.open(), yaml.SafeLoader)
            if "date" in local_meta:
                local_meta['date'] = datetime.date.fromisoformat(local_meta['date'])
            #print(local_meta)
            self.meta.update(local_meta)
            return
        
        except IOError:
            pass
        print(self.fn)
        syllabus_section = self.fn.replace("syllabus/", "")\
                           .replace(".md", "")
        if syllabus_section in syllabus_order:
            # Create a phony date for sorting syllabus sections,
            # at the start of the previous month.
            ix = syllabus_order.index(syllabus_section)
            y = datetime.date.today().year
            m = datetime.date.today().month
            m -= 1
            if m == 0:
                m = 12
                y = y - 1
            self.meta['date'] = datetime.date(y, m, 28 - ix)

    def build_doc_metadata(self):
        # Get metadata from three sources.
        self.infer_data_from_global_yaml()
        self.infer_data_from_local_yaml()        
        self.meta["toc"] = self.needs_html_toc()
        self.extract_yaml_header_to_meta()
        try:
            p = self.meta["date"]
        except KeyError:
            # Better if it's last modifed date.
            print("Warning--no date for {}".format(self.fn))
            self.meta["date"] = datetime.date.today()
            if self.fn.endswith("syllabus.md"):
                self.meta["date"] = self.meta["date"] - datetime.timedelta(90)
        if self.meta["title"]=="":
            basename = os.path.basename(self.fn)
            self.meta["title"] = basename.replace(".md","").replace("_"," ")

    def pdf_link_text(self):
        pdf_loc = self.rmd_loc().replace("_site/","").replace(".Rmd",".pdf")
        if pdf_loc.startswith("syllabus__"):
            pdf_loc = "syllabus.pdf"
        return "\n[Download PDF]({})\n\n\n".format(pdf_loc)

    def rmd_loc(self):
        return ("_site/" + self.fn.replace("/","__")).replace(".md",".Rmd")

    def build_needed_Rmd(self):
        new_file = self.rmd_loc()
        output = open(new_file,"w")

        output.write(yaml_header(self.meta))
        output.write(self.pdf_link_text())

        for line in self.lines:
            line = line.replace(r"```{r}",r"```")
            line = line.replace(r"```{R}",r"```")        
            output.write(line)

def build_index_file():
    doc_meta = course_settings
    #    doc_meta["title"] = doc_meta["Course_Title"]
#    doc_meta["title"] = doc_meta[""]    
    doc_meta["toc"] = "false"
    with open("_site/index.Rmd","w") as fout:
        fout.write(yaml_header(doc_meta))
        fout.write("\n\n")
        if os.path.exists(f"{dir}/index.md"):
            fout.write(open(f"{dir}/index.md").read().format(**doc_meta))


def yaml_header(doc_meta):
    if doc_meta is None:
        doc_meta["title"] = ""
    if not "title" in doc_meta:
        doc_meta["title"] = ""
    doc_meta["csl"] = Path("citationstyles/chicago-in-text.csl").resolve()
    doc_meta["bibliography"] = Path(f"{dir}/works_cited.bib").resolve()    
    return """---
title: "{title}"
bibliography: "{bibliography}"
csl: "{csl}"
output: 
  html_document:
    toc: {toc}
    toc_depth: 2
    toc_float: true
    theme: {web_theme}
...

""".format(**doc_meta)
