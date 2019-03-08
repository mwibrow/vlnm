"""
Some VLNM-specific stuff.
"""

import docutils.nodes
from docutils.parsers.rst import directives, Directive

import vlnm
from vlnm import get_normalizer, list_normalizers


class NormalizersDirective(Directive):
    """List normalizers in a table."""

    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = False

    def run(self):
        normalizers = list_normalizers()
        parent = docutils.nodes.paragraph()
        for name in normalizers:
            string_name = f"{name}"
            node = docutils.nodes.paragraph(string_name, string_name, classes=['monospace'])
            parent += node
        return [parent]


class MonospaceRole:
    """
        Class for processing the :rst:role:`tt`.
    """

    def __call__(self, typ, rawtext, text, lineno, inliner,
                 options=None, content=None):

        node = docutils.nodes.Element(rawtext, classes=['monospace'])

        return [node], []


def setup(app):
    """
    Set up the sphinx extension.
    """
    app.add_role('tt', MonospaceRole())
    app.add_directive('normalizers', NormalizersDirective)
