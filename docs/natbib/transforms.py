"""
    New Transforms
    ~~~~~~~~~~~~~~
"""

import docutils.transforms
import docutils.nodes

from .nodes import BibliographyNode, CitationNode
from .formatters.apa import ApaFormatter

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
        bibcache = env.bibcache.entries

        formatter = ApaFormatter()

        for bibnode in self.document.traverse(CitationNode):
            key = bibnode.data['keys'][0]
            refid = make_refid(bibcache[key], bibnode.data['docname'])
            node = formatter.make_citation(bibnode, bibcache, make_refid)
            bibnode.replace_self(node)

        for bibnode in self.document.traverse(BibliographyNode):
            node = docutils.nodes.paragraph()
            refid = make_refid(bibcache[key], bibnode.data['docname'])
            keys = formatter.sort_keys(env.bibkeys, bibcache)
            for key in keys:
                entry = formatter.make_entry(bibcache[key])
                entry['ids'] = entry['names'] = [refid]
                node += entry
            bibnode.replace_self(node)
