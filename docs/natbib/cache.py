"""
    Bibliography Cache
    ~~~~~~~~~~~~~~~~~~
"""


DOC_SEP = '~~~'
class BibliographyCache:
    """
    Class for caching bibliography files.
    """

    def __init__(self):
        self.cache = {}

    def add_entries(self, entries, docname):
        """
        Add bibliography data to the cache.
        """
        self.cache[docname] = self.cache.get(docname, {})
        for key in entries:
            self.cache[docname][key] = entries[key]

    def get_bibdata(self, docname):
        """Return bibdata for a document."""

    def __getitem__(self, key):
        if DOC_SEP in key:
            docname, citekey = key.split(DOC_SEP, 1)
            if docname in self.cache:
                return self.cache[docname][citekey]
        for docname in self.cache:
            if key in self.cache[docname]:
                return self.cache[docname][key]

        raise KeyError('Unknown key {}'.format(key))
