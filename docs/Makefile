
SRCDIR=source
BLDDIR=build
WATCH=-z ../vlnm -z ./$(SRCDIR) -z ./extensions/plots -z ./extensions/natbib -z ./extensions/console
CMDOPT=-E -a -d $(BLDDIR)/.doctrees

clean:
	rm -r $(BLDDIR)

html:
	sphinx-build $(CMDOPT) -b html  $(SRCDIR) $(BLDDIR)

watch:
	sphinx-autobuild $(WATCH) $(CMDOPT) -b html  $(SRCDIR) $(BLDDIR)
