"""
Some VLNM-specific stuff.
"""

import docutils.nodes
import docutils.utils
from docutils.parsers.rst import directives, Directive, languages
from docutils.parsers.rst.states import NestedStateMachine, Inliner, Struct

from sphinx.parsers import RSTParser

import vlnm
from vlnm import get_normalizer, list_normalizers


class NormalizersDirective(Directive):
    """List normalizers in a table."""

    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = False

    def run(self):
        document = self.state.document
        language = languages.get_language(document.settings.language_code)

        normalizers = list_normalizers()
        parent = docutils.nodes.paragraph()

        string_name = ''
        for name in normalizers:
            string_name += f" ``{name}``, "
            klass = get_normalizer(name)
            string_name += f" :class:`{klass.__name__} <{klass.__module__}.{klass.__name__}>` , "
        tmpdoc = docutils.utils.new_document('', document.settings)
        parser = RSTParser()
        parser.parse(string_name, tmpdoc)
        parent += tmpdoc.children[0].children
        return [parent]


def setup(app):
    """
    Set up the sphinx extension.
    """
    app.add_directive('normalizers', NormalizersDirective)
