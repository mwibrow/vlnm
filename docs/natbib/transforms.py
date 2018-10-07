"""
    New Transforms
    ~~~~~~~~~~~~~~
"""

import docutils.transforms
import docutils.nodes

from .nodes import BibliographyNode, CitationNode
from .formatters.authoryear import AuthorYearFormatter

def make_refid(entry, docname):
    """
    Make an id for a uri.
    """
    if docname:
        return '{}-{}'.format(entry.key, docname)
    return entry.key


class BibliographyTransform(docutils.transforms.Transform):
    """
    Transform bibliography nodes.
    """
    # transform must be applied before references are resolved
    default_priority = 10

    def apply(self, **_):
        """
        Apply the transform
        """
        env = self.document.settings.env
        bibcache = env.bibcache

        for bibnode in self.document.traverse(BibliographyNode):
            docname = bibnode.data['docname']

            formatter = AuthorYearFormatter()

            node = docutils.nodes.paragraph()
            keys = formatter.sort_keys(env.bibkeys, bibcache)
            for key in keys:
                refid = make_refid(bibcache[key], bibnode.data['docname'])
                entry = formatter.make_entry(bibcache[key])
                entry['ids'] = entry['names'] = [refid]
                node += entry
            bibnode.replace_self(node)

            for citenode in self.document.traverse(CitationNode):
                if citenode.data['docname'] == docname:
                    node = formatter.make_citation(
                        citenode, bibcache, make_refid)
                    citenode.replace_self(node)
