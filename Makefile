### Special options

content_root=course

config_file = $(content_root)/course.yml

bibLocation=$(content_root)/works_cited.bib
pandocOptions=--template=templates/template.tex --bibliography=$(bibLocation) --csl=citationstyles/chicago-in-text.csl
course_code=$(shell cat $(config_file) | shyaml get-value Code)

# All md files beginning with a capital letter should become PDFs, except README.md and anything in Readings
# Lectures are handled spearately

MARKDOWNS=$(shell find $(content_root) -iname '*.md' -not -path "$(content_root)/Lectures/*" -not -path "$(content_root)/Readings/*" -not -path "$(content_root)/private/*" -not -path "$(content_root)/syllabus/*" | egrep -v "\#" | sed 's/ /\\ /g' | grep -v "^[a-z0-9]")

PDFS=$(patsubst %.md,%.pdf,$(MARKDOWNS))

WEBPDFS=$(filter-out _site/Lectures.pdf _site/Readings.pdf, $(shell find . -name ".pdflist.tmp" | xargs cat))

LECTURES=$(patsubst %.md,%.pdf,$(shell find -L $(content_root)/Lectures -name '*.md' -not -path "*\#*"))
LECTURESEPUB=$(patsubst %.md,%.epub,$(shell find -L $(content_root)/Lectures -name '*.md' -not -path "*\#*"))
outlines=$(addprefix $(content_root)/Lectures/outlines/,$(notdir $(LECTURES)))
slides=$(addsuffix .html,$(basename $(addprefix _site/slides/,$(notdir $(LECTURES)))))
cached_images = $(patsubst $(content_root)/Lectures/%.pdf, $(content_root)/images/%, $(LECTURES))

# Readings will always be pdf or mp3 files to be uploaded to the web site.
Readings=$(shell find $(content_root)/Readings -regex '.*\(.pdf\|.mp3\)' | sed 's/ /\\ /g')

SYLLABUS_SECTIONS=$(shell cat $(content_root)/syllabus/order.yml | xargs -I{} -n 1 ls $(content_root)/syllabus/{}.md)

all:  $(bibLocation) templates/configuration.tex $(PDFS) glimpse website $(content_root)/syllabus/syllabus.pdf compiledLectures

cache_the_images: $(cached_images)

pdfoutlines: $(outlines)

pdfs: $(PDFS) $(WEBPDFS) $(outlines)

syllabus: $(content_root)/syllabus/syllabus.pdf

slides: $(slides)

glimpse: $(MARKDOWNS)
# Convenience; print an outline of the last edited Markdown file.
	@ls -t -1 $(content_root)/Lectures | grep "md" | head -1 | xargs -I {} pandoc --filter /usr/local/bin/lectureToOutline -t markdown $(content_root)/Lectures/{} | grep "."

compiledLectures: $(LECTURESEPUB) $(slides)

test:
	@echo "SYLLABUS SECTIONS\n------------------"
	@echo $(SYLLABUS_SECTIONS)
	@echo "PDFS\n------------------"
	@echo $(PDFS)
	@echo "WEBPDFS\n------------------"
	@echo $(WEBPDFS)
	@echo "MARKDOWNS\n------------------"
	@echo $(MARKDOWNS)


###################
## Website rules ##
###################

upload: all  $(WEBPDFS) pdfoutlines
	rsync -ra _site/ root@benschmidt.org:html/${course_code}/

website: $(config_file) _site _site/index.html _site/syllabus.pdf _site/slides $(WEBPDFS) $(slides) $(outlines)
	@mkdir -p _site/Readings/Readings/
	rsync -ra $(content_root)/Readings/ _site/Readings/Readings/
	rsync -ra $(content_root)/Lectures/outlines/ _site/

_site:
	mkdir -p _site

_site/slides: $(slides) $(content_root)/images/
	mkdir -p _site
	rsync -ra templates/slides/ _site/slides/
	chmod -R 755 $(content_root)/images/
	rsync -ra $(content_root)/images/ _site/slides/images/

_site/index.html: $(config_file) $(MARKDOWNS) _site $(SYLLABUS_SECTIONS)# $(content_root)/Readings/Readings.md
	python scripts/build_site_components.py
	Rscript -e "setwd('_site'); rmarkdown::render_site(quiet = TRUE)"
        # ???
	rsync -r _site/_site/ _site/

_site/%.pdf: _site
	@make $(content_root)/$(subst __,/,$*.pdf)
	@cp $(content_root)/$(subst __,/,$*.pdf) $@

_site/Lecture.pdfs:
# This is just a dummy.
# Is it supposed to end with 'pdfs'?
	echo "WHAAT"
	touch $@

_site/syllabus.pdf: $(content_root)/syllabus/syllabus.pdf _site
	@cp $< $@

#So: to make a part appear in the syllabus, it just has to be a markdown file starting with a number.

$(content_root)/Readings/Readings.md: #$(content_root)/Readings
	ls -t $< | perl -ne 'chomp; $$line = $$_; if ($$_ =~ m/((.*).(pdf|mp3))/g) {my $$basename= $$1;$$basename =~ s/_/ /g; print "[$$basename](/Readings/$$_)\n\n"}' > $@

$(content_root)/images/%: $(content_root)/Lectures/%.md
	mkdir $@
	python scripts/download_images.py $< $@

templates/configuration.tex: $(config_file)
	python scripts/make_config.py

###################
## Bibliography ###
###################

$(content_root)/.pathkeys: $(SYLLABUS_SECTIONS) $(MARKDOWNS)
	python scripts/list_bibliography_keys.py

$(bibLocation): $(content_root)/.pathkeys
	python scripts/create_bibliography.py

##################
#### Syllabus ####
##################

$(content_root)/syllabus/Schedule.md: $(content_root)/syllabus/schedule.yml
	python scripts/parse_schedule.py $< $@

$(content_root)/meetings.yml: $(content_root)/syllabus/schedule.yml
	python scripts/parse_schedule.py

$(content_root)/syllabus/syllabus.pdf: $(content_root)/syllabus/syllabus.md templates/configuration.tex  $(config_file) $(bibLocation)
	pandoc --pdf-engine=xelatex -o $@ $(pandocOptions) --variable syllabus=T $<

$(content_root)/syllabus/%.pdf: templates/configuration.tex $(content_root)/syllabus/%.md $(bibLocation)
	pandoc  --pdf-engine=xelatex -o $@ $(pandocOptions) $< $(config_file)

$(content_root)/syllabus/syllabus.md: $(content_root)/syllabus/Schedule.md $(SYLLABUS_SECTIONS) $(content_root)/syllabus/schedule.yml $(content_root)/syllabus/order.yml
# For the printed syllabus, drop headers a level and make the title
# a section heading. This could be done properly in pandoc, but isn't.
	@pandoc  $(config_file) $(SYLLABUS_SECTIONS) -t markdown | perl -pe ' s/^#/\n##/; s/^% /\n\n# /' > $@
#	echo "$(SYLLABUS_SECTIONS)" | tr " " "\n" | xargs 

$(content_root)/syllabus/order.yml:
	ls $(content_root)/syllabus/ | grep md | grep -v syllabus | perl -pe 's/.md.?//' | uniq > $(content_root)/syllabus/order.yml

##############
## Lectures ##
##############

$(content_root)/Lectures/%.yml:
	echo "$*" | xargs printf '---\ntitle: "%s"\n\n...' > $@

$(content_root)/Lectures/outlines/%.pdf: $(content_root)/Lectures/%.yml $(config_file) $(content_root)/Lectures/%.md
	@mkdir -p $(content_root)/Lectures/outlines/
	@echo "$@"
	@pandoc --pdf-engine=xelatex --filter /usr/local/bin/lectureToOutline $(pandocOptions) -o $@ $^
	@cp $@ _site/

$(content_root)/Lectures/%.epub: $(content_root)/Lectures/%.yml $(config_file) $(content_root)/Lectures/%.md
	pandoc --bibliography=$(bibLocation) --filter /usr/local/bin/lectureToPrintable -o $@ $^

$(content_root)/Lectures/%.pdf: $(content_root)/Lectures/%.yml $(config_file) $(content_root)/Lectures/%.md
	pandoc --pdf-engine=xelatex -o $@ $(pandocOptions) --filter /usr/local/bin/lectureToPrintable $(config_file) $^

############
##  PDFS  ##
############

%.pdf: %.md $(config_file) works_cited.bib
	echo $@
	pandoc  --pdf-engine=xelatex -o $@ $(pandocOptions) $< $(config_file)

$(content_root)/tests/%.pdf: %.md $(config_file) $(bibLocation)
	echo "Building with base format"
	pandoc  --pdf-engine=xelatex -o $@ --filter /usr/local/bin/shuffleAllLists $(pandocOptions) $< $(config_file)

clean:
	rm templates/configuration.tex
	rm -f $(content_root)/syllabus/*.pdf $(content_root)/syllabus/syllabus.pdf $(content_root)/syllabus/syllabus.md  $(content_root)/syllabus/Schedule.md
	rm -rf _site/*	
	rm -rf $(PDFS)
	rm -rf $(PUBS)
	rm -rf $(content_root)/Lectures/*.yml $(content_root)/Lectures/*.pdf $(content_root)/Lectures/*.pdf
	rm -rf $(content_root)/Lectures/outlines

##############
### site #####
##############

_site/slides/%.html: $(content_root)/Lectures/%.yml $(config_file) $(content_root)/Lectures/%.md
	mkdir -p _site/slides
	@echo $*
	@pandoc --filter /usr/local/bin/lectureToSlidedeck --slide-level=2 -V theme=night -t revealjs --template templates/revealjs.html --variable=transition:Slide $^ > $@


