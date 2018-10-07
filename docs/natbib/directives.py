"""
    New Directives
    ~~~~~~~~~~~~~~
"""

import os

from pybtex.database.input import bibtex
from docutils.parsers.rst import directives, Directive

from .nodes import BibliographyNode

class BibliographyDirective(Directive):
    """Class for processing the :rst:dir:`bibliography` directive.
    """
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = False
    option_spec = {
        'style': directives.unchanged
    }

    def run(self):
        """Process .bib files, set file dependencies, and create a
        node that is to be transformed to the entries of the
        bibliography.
        """
        env = self.state.document.settings.env

        id_ = 'bibtex-bibliography-{}-{}'.format(
            env.docname, env.new_serialno('bibtex'))
        for bibfile in self.arguments[0].split():

            bibfile = os.path.normpath(env.relfn2path(bibfile.strip())[1])
            parser = bibtex.Parser()
            bibcache = parser.parse_file(bibfile)

        env.bibcache = bibcache
        data = dict(
            docname=env.docname,
            style=self.options.get('style'))
        return [BibliographyNode('', ids=[id_], data=data)]
