SRCDIR=source
BLDDIR=build
DISTDIR=dist
OUTDIR=html
GH_PAGES=$(DISTDIR)/gh-pages
HTMLDIR=$(shell pwd)/$(DISTDIR)/$(OUTDIR)
EXTENSIONS=-z ./extensions
WATCH=-z ../vlnm -z ./$(SRCDIR) $(EXTENSIONS)
CMDOPT=-E -a -d $(BLDDIR)/.doctrees
IGNORE=-i *.csv -i *.tsv
SPHINXBUILD=python3 -m sphinx

html:
	$(SPHINXBUILD) $(CMDOPT) -b html  $(SRCDIR) $(BLDDIR)/html

watch:
	sphinx-autobuild $(WATCH) $(IGNORE) $(CMDOPT) -b html  $(SRCDIR) $(BLDDIR)/$(OUTDIR)

dist: clean-dist
	export SPHINX_SASS_SOURCE_MAPS=FALSE; \
	$(SPHINXBUILD) -E -a -d $(DISTDIR)/.doctrees -b html $(SRCDIR) $(DISTDIR)/$(OUTDIR)

gh-pages: dist
	@mkdir -p $(GH_PAGES); \
	(	\
		cd $(GH_PAGES); \
		git clone `git config --get remote.origin.url`; \
		cd `ls`; \
		git checkout -B gh-pages; \
		rm -rf `find . | grep -v "^\([.]\+\|[.]/[.]git.*\)$$"`; \
		cp -R "$(HTMLDIR)"/* .; \
		touch .nojekyll; \
		git add .; \
		git commit -a -m "Update gh-pages"; \
		git push -f origin gh-pages; \
	);

clean: clean-build clean-dist

clean-build:
	@if [ -d "$(BLDDIR)" ]; then \
		chmod -R u+rwx $(BLDDIR); \
		rm -r $(BLDDIR); \
	fi;

clean-dist:
	@if [ -d "$(DISTDIR)" ]; then \
		chmod -R u+rwx $(DISTDIR); \
		rm -r $(DISTDIR); \
	fi;

clean-gh-pages:
	@if [ -d "$(GH_PAGES)" ]; then \
		chmod -R u+rwx $(GH_PAGES); \
		rm -rf $(GH_PAGES); \
	fi

