
SRCDIR=source
BLDDIR=build
WATCH=-z ../vlnm -z ./$(SRCDIR)
CMDOPT=-E -a -d $(BLDDIR)/.doctrees

clean:
	rm -r $(BLDDIR)

html:
	sphinx-build $(CMDOPT) -b html  $(SRCDIR) $(BLDDIR)

watch:
	sphinx-autobuild $(WATCH) $(CMDOPT) -b html  $(SRCDIR) $(BLDDIR)

nodemon:
	(cd $(BLDDIR) && http-server) & \
	nodemon --ext py,rst,bib --ignore ./$(BLDDIR) --exec "make html" --verbose
