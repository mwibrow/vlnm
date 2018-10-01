
SRCDIR=source
BLDDIR=build
WATCH=-z ../vlnm
CMDOPT=$(WATCH) -E -a -d $(BLDDIR)/.doctrees

clean:
	rm -r $(BLDDIR)

html:
	sphinx-build $(CMDOPT) -b html  $(SRCDIR) $(BLDDIR)

watch:
	sphinx-autobuild $(CMDOPT) -b html  $(SRCDIR) $(BLDDIR)
