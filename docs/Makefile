
SRCDIR=source
BLDDIR=build
EXTENSIONS=-z ./extensions/plots -z ./extensions/natbib -z ./extensions/console -z ./extensions/tables
WATCH=-z ../vlnm -z ./$(SRCDIR) $(EXTENSIONS)
CMDOPT=-E -a -d $(BLDDIR)/.doctrees

clean:
	rm -r $(BLDDIR)

html:
	sphinx-build $(CMDOPT) -b html  $(SRCDIR) $(BLDDIR)

watch:
	sphinx-autobuild $(WATCH) $(CMDOPT) -b html  $(SRCDIR) $(BLDDIR)
