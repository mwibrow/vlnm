"""
    Base Formatter class
    ~~~~~~~~~~~~~~~~~~~~
"""

# pylint: disable=no-self-use,unused-argument

class Formatter:
    """
    Class for creating citations and bibliographic entries in the APA style.
    """
    def __init__(self):
        self.nodes = []
        self.publications = {}

    @staticmethod
    def sort_keys(keys, bibcache):
        """
        Return a sort key for sorting the bibliography
        """
        if bibcache:
            return keys
        return keys

    def make_entry(self, ref):
        """
        Make a bibliographic entry.
        """
        return ref

    def make_citation(self, bibnode, bibcache, make_refid):
        """
        Create a reference for a citation.
        """

        return bibnode
