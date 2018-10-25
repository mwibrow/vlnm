"""
    New Transforms
    ~~~~~~~~~~~~~~
"""

import docutils.transforms
import docutils.nodes

from .nodes import BibliographyNode, CitationNode
from .formatters.authoryear import AuthorYearFormatter


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
            keys = env.bibkeys.get_keys(docname)
            formatter = AuthorYearFormatter()

            node = docutils.nodes.paragraph()
            keys = formatter.sort_keys(keys, bibcache)

            year_suffixes = formatter.resolve_ties(keys, bibcache)
            for key in year_suffixes:
                bibcache[key].fields['year_suffix'] = year_suffixes[key]

            for key in keys:
                refid = '{}'.format(key)
                entry = formatter.make_entry(bibcache[key])
                entry['ids'] = entry['names'] = [refid]
                node += entry
            bibnode.replace_self(node)

            for citenode in self.document.traverse(CitationNode):
                if citenode.data['docname'] == docname:
                    node = formatter.make_citation(
                        citenode, bibcache, docname)
                    citenode.replace_self(node)

            for key in year_suffixes:
                bibcache[key].fields['year_suffix'] = ''
