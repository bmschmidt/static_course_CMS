import md_tools
import os
import re
import yaml
import dateutil
import datetime
import sys
from settings import dir, course_settings, get_course
from pathlib import Path
course = course_settings

def build_yaml(write = True):
    output = {}
    output["name"] = course["Course_Title"]
    output["navbar"] = {}
    output["navbar"]["title"] = course["Course_Number"]
    site_list = files_in_dir(dir, render_too = True)
    if course['course_type'] == "syllabus_only":    
        double_linked = []
        for l in site_list:
            if 'menu' in l and l['text'] == 'Syllabus':
                double_linked = l['menu']
        site_list = double_linked

    output["navbar"]["left"] = site_list
    
    if write:
        f = open("_site/_site.yml", "w")
        f.write(yaml.dump(output))

    return site_list

def write_pdf_list(site_list):
    
    pdfs = []
    
    for item in site_list:
        if "href" in item:
            pdfs.append(("_site/" + item['href']).replace(".html",".pdf"))
        if "menu" in item:
            for itemm in item["menu"]:
                if "href" in itemm:
                    try:
                        pdfs.append(("_site/" + itemm['href']).replace(".html",".pdf"))
                    except:
                        print("\n\n\n")
                        raise
    with open(".pdflist.tmp","w") as f:
        pdfs = [fn for fn in pdfs if not fn.startswith("_site/syllabus") and not fn.endswith("Readings.pdf")]
        pdfs.append("_site/syllabus.pdf")
        f.write(" ".join(pdfs) + "\n")
                

def files_in_dir(dir, render_too = False):
    # Find markdown files in a directory.
    hits = []
    subfolders = [x for x in dir.iterdir() if x.is_dir()]
    subfolders.sort()
    all_docs = []
    for sf in subfolders:
        name = sf.name
        if "exclude_dirs" in course:
            if name in course["exclude_dirs"] or sf=="Readings":
                continue
        if not re.search("^[A-Z]|syllabus",name):
            continue
        hits.append({"text": name.replace("syllabus","Syllabus")})
        if os.path.exists(name + "_index.md"):
            hits[-1]["href"] = name + "_index.html"
        mds = [f.name for f in sf.iterdir() if f.name.endswith(".md")]
        mds.sort()
        if len(mds) > 0:
            hits[-1]["menu"] = []
            
        def get_meta_and_build(md):
            oo = md_tools.MarkdownFile(Path(sf, md))
            oo.build_needed_Rmd()
            ddate = oo.meta["date"]
            return (ddate, md, oo)
        
        meta_mds = list(map(get_meta_and_build, mds))
        
        # Sort on date, then name.
        meta_mds.sort()
        for ddate, md, oo in meta_mds:
            if oo.hidden():
                continue
            label = md.replace(".md", "").replace("_"," ")
            label.replace("syllabus", " Full syllabus")
            hits[-1]["menu"].append({
                "text": label,
                "href":name + "__" + md.replace(".md",".html")
            })
            all_docs.append(name + "__" + md.replace(".md",".html"))
            
    l = build_lectures()
    r = build_readings()
    
    if l:
        hits.append({"text":"Lectures outlines and slides", "href":"Lectures.html"})
    if r:
        hits.append({"text":"Readings", "href":"Readings.html"})
    
    return hits


def build_lectures(just_list = False):
    try:
        lecture_files = Path("course/Lectures").glob("*.md")
    except:
        return False
        
    all_lectures = []
    for f in lecture_files:
        try:
            lecture = md_tools.MarkdownFile(f)
        except IOError:
            print("Error on {}".format(f))
            continue
        if lecture.hidden():
            continue
        tuple = (lecture.meta["date"], lecture.title(), lecture)
        all_lectures.append(tuple)
    all_lectures.sort()
    if just_list:
        return all_lectures
    doc_meta = {k:v for k,v in course.items()}
    doc_meta["title"] = "Lecture links and outlines"
    doc_meta["toc"] = "false"

    header = md_tools.yaml_header(doc_meta)

    oput = open("_site/Lectures.Rmd","w")
    oput.write(header)

    for date,title, lecture in all_lectures:
        p = os.path.basename(lecture.fn).replace(".md","")
        oput.write("* {} [(outline)](outlines/{}.pdf) [(slides)](slides/{}.html)\n".format(
            title,p,p
        ))
    return lecture_files

def build_readings(just_list = False):
    try:
        readings = os.listdir("Readings")
    except:
        return False

    reading_files = ["Readings/" + f for f in readings if f.endswith("pdf")]
    
    all_readings = []
    for f in reading_files:
        all_readings.append(f)
    all_readings.sort()
    if just_list:
        return all_readings
    doc_meta = get_course()
    doc_meta["title"] = "Reading links and outlines"
    doc_meta["toc"] = "false"

    header = md_tools.yaml_header(doc_meta)

    oput = open("_site/Readings.Rmd","w")
    oput.write(header)

    for r in all_readings:
        p = os.path.basename(r).replace(".pdf","")
        oput.write("* [{}](Readings/{})\n".format(p, r))

    return reading_files

def build_site():
    site_list = build_yaml()
    write_pdf_list(site_list)
    build_lectures()
    md_tools.build_index_file()

    
no_pdfs = set(["course/" + x for x in ["Readings/Readings.md"]])
def files(format = 'markdown'):
    """
    returns PosixPath
    """
    ordinary = [f for f in Path("course").glob("*/*.md") if not str(f) in no_pdfs and not "Lectures/" in str(f)]
    lectures = [f for f in Path("course", "Lectures").glob("*.md") if not str(f) in no_pdfs]
    
    if format == 'markdown':
        return [str(f) for f in ordinary + lectures]

    outlines = [ Path("course", "Lectures", "outlines", f.name.replace(".md", ".pdf")) for f in lectures]
    
    if format == 'slides':
        return [Path("_site", "slides", f.name.replace(".md", ".html")) for f in lectures]
    elif format == 'epub':
        return [f.with_suffix(".epub") for f in lectures]
    elif format == 'pdf':
        return [f.with_suffix(".pdf") for f in ordinary + lectures] + outlines
    elif format == 'webpdf':
        
        base = [Path("_site", "__".join(f.with_suffix(".pdf").parts[1:])) for f in ordinary]
        outlines = [Path("_site", "outlines", l.name.replace(".md", ".pdf")) for l in lectures]
        
        return base + outlines
    return fs

if __name__=="__main__":
    try:
        argument = sys.argv[1]
    except IndexError:
        raise NameError("Usage: python scripts/build_site_components.py ARG\n"
              "where ARG is one of 'build', 'markdown', 'pdfs', 'webpdfs'")
    try:
        future = sys.argv[2]
    except:
        future = False
    if argument == 'build':
        build_site()
    elif argument in ['markdown', 'pdf', 'webpdf', 'epub', 'slides']:
        names = [str(f) for f in files(argument)]
        print(' '.join(names))
    else:
        print ("No sensible args")
