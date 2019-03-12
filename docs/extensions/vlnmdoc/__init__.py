"""
Some VLNM-specific stuff.
"""

import importlib
import re

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
        # language = languages.get_language(document.settings.language_code)

        normalizers = sorted(list_normalizers())
        parent = docutils.nodes.paragraph()

        input_lines = [
            '',
            '',
            '.. list-table:: Vowel normalizers implmented in |vlnm|',
            '    :header-rows: 1',
            '    :align: center',
            '    :class: normalizers',
            '',
            '    * - Normalizer',
            '      - Vowel',
            '      - Formant',
            '      - Speaker']

        def _mkcls(cls):
            return (cls or '').capitalize() or 'N/A'
        for name in normalizers:
            klass = get_normalizer(name)
            input_lines.append(f'    * - :ref:`{name} <{name}>`')
            classify = klass.classify or {}
            input_lines.extend([
                f"      - {_mkcls(classify.get('vowel'))}",
                f"      - {_mkcls(classify.get('formant'))}",
                f"      - {_mkcls(classify.get('speaker'))}"
            ])
        input_lines.append('')
        input_lines = [f'        {input_line}' for input_line in input_lines]
        input_lines = '\n'.join(input_lines)

        parser = RSTParser()
        parser.parse(input_lines, document)

        return [parent]


class NormalizerSummariesDirective(Directive):
    """Summarize normalizer documentation."""

    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = False

    def run(self):
        document = self.state.document
        names = sorted(list_normalizers())
        modules = {}
        for name in names:
            klass = get_normalizer(name)
            module = klass.__module__
            if module in modules:
                modules[module].append(klass)
            else:
                modules[module] = [klass]

        module_names = sorted(list(modules.keys()))

        nodes = []
        for module_name in module_names:
            module = importlib.import_module(module_name)
            module_title = module.__doc__.strip().split('\n')[0]
            module_doc = '\n'.join(module.__doc__.strip().split('\n')[2:])
            input_lines = [f'.. rubric:: {module_title}', '   :class: module', module_doc, '']
            for klass in modules[module_name]:
                name = klass.name
                markup = f':obj:`{name}`'
                input_lines.extend(
                    ['', f'.. _{name}:', '', f'.. rubric:: {markup}', '   :class: name', ''])
                doc = reindent(klass.__doc__)
                summary = doc_summary(doc)
                input_lines.extend(summary)
                input_lines.extend([
                    '',
                    f'The :obj:`{name}` normalizer is implemented in the '
                    f':class:`{klass.__name__} <{module.__name__}.{klass.__name__}>` class.'
                ])

            input_lines = '\n'.join(input_lines)
            parser = RSTParser()
            parser.parse(input_lines, document)

        return nodes


def doc_summary(lines):
    """Extract summary of docs."""
    summary = []
    for line in lines:
        if line.startswith('Parameters') or line.startswith('Example'):
            break
        summary.append(line)
    return summary


def reindent(docstring):
    """Reindent docstring."""
    lines = docstring.split('\n')
    indent = 0
    for line in lines:
        match = re.match(r'^(\s{4})+', line)
        if match:
            indent = match.end()
            break
    lines = [line[indent:] if line.startswith(' ' * indent) else line for line in lines]
    return lines


def setup(app):
    """
    Set up the sphinx extension.
    """
    app.add_directive('normalizers', NormalizersDirective)
    app.add_directive('summaries', NormalizerSummariesDirective)
