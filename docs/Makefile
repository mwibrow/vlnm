SRCDIR=source
BLDDIR=build
EXTENSIONS=-z ./extensions
WATCH=-z ../vlnm -z ./$(SRCDIR) $(EXTENSIONS)
CMDOPT=-d $(BLDDIR)/.doctrees
IGNORE=-i *.csv -i *.tsv

clean:
	rm -r $(BLDDIR)

html:
	sphinx-build -E -a $(CMDOPT) -b html  $(SRCDIR) $(BLDDIR)

watch: html
	sphinx-autobuild -E -a $(WATCH) $(IGNORE) $(CMDOPT) -b html  $(SRCDIR) $(BLDDIR)

api-doc:
	sphinx-apidoc -f -o $(SRCDIR)/api ../vlnm
