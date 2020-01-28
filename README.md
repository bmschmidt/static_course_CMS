Truly Static Course Management System
=================

This is a set of scripts and templates for maintaining course files in Markdown and Pandoc
and exporting them (as needed) to HTML for a website. I

The basic workflow is:

1. Write a Markdown file, and put it in a **content folder**.
2. Run the makefile.
3. Build a course website in a folder called `_site`.
3. Watch as the file is uploaded to the course website through pandoc


The core pdf templates are by Andrew Goldstone.

Dependencies
============

This requires some fiddly command line stuff.

* R with knitr is used to compile the site to HTML.
* Pandoc version 2.3 (IIRC) or higher with some [custom extension scripts I wrote](https://github.com/bmschmidt/MarkdownLectures)
  to work with lectures and outlines.
* A full latex stack to make pdfs.
* python3 to run the various script in `scripts`. I don't really plan to make them easier to reproduce.

So that's right--to fully work with this, you get to work in R, Python, Makefile, and Haskell. I plan to add something using node soon.



Content Folder
=======

The course lives in a folder called `course/`. It's not part of this repository; I'll have some examples online, though.

Folders that begin with capital letters (`Handouts/`,`Assignments/`, etc.) are
the **content folders** for the class. Any file place in one of those. They become links for the website.

Syllabus
-------

There must be a folder called `syllabus/`. It contains markdown files; eg, Grading, Requirements.

* The schedule is built from a yaml file. That doesn't have dates in it: instead, you enter the days and semester for a class and they're parsed from the `calendars.yml` file which handles things like breaks. 


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

