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

        normalizers = sorted(list_normalizers())
        parent = docutils.nodes.paragraph()

        input_lines = [
            '',
            '.. role:: red'
            '',
            '.. list-table:: classify of vowel normalizers',
            '    :header-rows: 1',
            '    :align: center',
            '    :class: normalizers',
            '',
            '    * - Normalizer',
            '      - Python class',
            '      - Vowel',
            '      - Formant',
            '      - Speaker']

        def _mkcls(cls):
            return (cls or '').capitalize() or 'N/A'
        for name in normalizers:
            klass = get_normalizer(name)
            link = f'{klass.__module__}.{klass.__name__}'
            input_lines.append(f'    * - ``{name}``')
            input_lines.append(f'      - :class:`{klass.__name__}  <{link}>`')
            classify = klass.classify or {}
            vowel = ()
            input_lines.extend([
                f"      - {_mkcls(classify.get('vowel'))}",
                f"      - {_mkcls(classify.get('formant'))}",
                f"      - {_mkcls(classify.get('speaker'))}"
            ])
        input_lines.append('')
        input_lines = [f'        {input_line}' for input_line in input_lines]
        input_lines = '\n'.join(input_lines)

        tmpdoc = docutils.utils.new_document('', document.settings)
        parser = RSTParser()
        parser.parse(input_lines, tmpdoc)
        parent += tmpdoc.children[0].children
        return [parent]


def setup(app):
    """
    Set up the sphinx extension.
    """
    app.add_directive('normalizers', NormalizersDirective)
