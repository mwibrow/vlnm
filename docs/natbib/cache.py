"""
    Bibliography Cache
    ~~~~~~~~~~~~~~~~~~
"""
from orderedset import OrderedSet

class CitationCache:
    """
    Class for caching citation keys
    """

    def __init__(self):
        self.cache = {}

    def add_key(self, key, docname):
        """
        Add a key to the cache for a document.
        """
        cache = self.cache.get(docname, OrderedSet())
        cache.add(key)
        self.cache[docname] = cache

    def add_keys(self, keys, docname):
        """
        Add a key to the cache for a document.
        """
        for key in keys:
            self.add_key(key, docname)

    def get_keys(self, docname=None):
        """
        Return the keys for a document.
        """
        if docname:
            try:
                return list(self.cache[docname])
            except KeyError:
                return []
        keys = []
        for doc in self.cache:
            keys.extend(self.cache[doc])
        return keys


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
