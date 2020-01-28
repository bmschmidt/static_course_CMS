Course Management
=================

This is a set of templates for maintaining course files in Markdown and Pandoc
and exporting them (as needed) to HTML for a website. It's built up off the
syllabus files Andrew Goldstone created for his courses at Rutgers; the chief
difference is that the root level is designed to hold all other paper documents
distributed in the course.

The basic workflow is:

1. Write a Markdown file, and put it in a **content folder**.
2. Run the makefile.
3. Build a course website in a folder called `_site`.
3. Watch as the file is uploaded to the course website through pandoc


Dependencies
============

This requires some fiddly command line stuff.

* R with knitr is used to compile the site to HTML.
* Pandoc version 2.3 (IIRC) or higher with some [custom extension scripts I wrote](https://github.com/bmschmidt/MarkdownLectures)
  to work with lectures and outlines.
* A full latex stack to make pdfs.




Content Folder
=======

Folders that begin with capital letters (`Handouts/`,`Assignments/`, etc.) are
the **content folders** for the class. Any file place in one of those. They become links for the website.

Syllabus
-------

There must be a folder called `syllabus/`. It contains numbered markdown files; eg, 4-Schedule.


Lectures
--------

Files in `Lectures/` are treated specially. The raw markdown files are your
lecture notes.

They will be parsed using the Markdown Lectures script so that there are both
instructor notes, and

Index
------

The contents of the splash page are written manually in `index.md`. You could edit this.




Configuration of Global variables
=================================

course.yml is a configuration file containing a number of course-specific
variables like instructor name, course number, and so forth. These are included
at the head of all documents for the course.

Makefile
========

A simple "make" command should compile all Markdown files in the root directory
into pdfs. It will also try to regenerate the syllabus if files are missing.

