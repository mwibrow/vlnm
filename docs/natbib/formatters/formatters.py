"""
    Base Formatter class
    ~~~~~~~~~~~~~~~~~~~~
"""

# pylint: disable=no-self-use,unused-argument
import re

from .nodes import (
    call, emph, field, join, optional, text)


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



def dashify(string, dash='–'):
    """Replace dashes with unicode dash."""
    return re.sub(r'-+', dash, string)

year = join['(', field['year'], ')']
pages = call[dashify, field['pages']]