"""
Some VLNM-specific stuff.
"""
import re

import docutils.nodes
from docutils.parsers.rst import directives
import docutils.utils
import docutils.statemachine
from sphinx.util.docutils import SphinxDirective

from vlnm import get_normalizer, list_normalizers


class NormalizersTableDirective(SphinxDirective):
    """List normalizers in a table."""

    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    has_content = False

    def run(self):
        document = self.state.document
        tab_width = document.settings.tab_width

        normalizers = sorted(list_normalizers())
        input_lines = [
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

        raw_text = '\n'.join(input_lines)
        include_lines = docutils.statemachine.string2lines(
            raw_text, tab_width, convert_whitespace=True)
        self.state_machine.insert_input(include_lines, '')
        return []


class NormalizersListDirective(SphinxDirective):
    """List normalizers in a module."""

    require_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    has_content = False

    option_spec = {
        'module': directives.unchanged
    }

    def run(self):
        document = self.state.document
        tab_width = document.settings.tab_width

        module = self.options.get('module', 'vlnm')
        names = list_normalizers(module=module)
        input_lines = [
            'The following normalizers are implemented in the ``{module}`` module:'.format(
                module=module)
        ]
        for name in names:
            klass = get_normalizer(name)
            input_lines.append(
                '{tab}* :class:`{klass} <{module}.{klass}>`'.format(
                    tab=' ' * tab_width,
                    klass=klass.__name__,
                    module=klass.__module__
                ))

        raw_text = '\n'.join(input_lines)
        include_lines = docutils.statemachine.string2lines(
            raw_text, tab_width, convert_whitespace=True)
        self.state_machine.insert_input(include_lines, '')

        return []


class NormalizerSummariesDirective(SphinxDirective):
    """Summarize normalizer documentation."""

    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = False

    def run(self):
        document = self.state.document
        tab_width = document.settings.tab_width

        names = sorted(list_normalizers())
        modules = {}
        for name in names:
            klass = get_normalizer(name)
            module = klass.__module__
            if module in modules:
                modules[module].append(klass)
            else:
                modules[module] = [klass]

        # module_names = sorted(list(modules.keys()))
        # for module_name in module_names:
            # module = importlib.import_module(module_name)
            # module_title = module.__doc__.strip().split('\n')[0]
            # module_doc = '\n'.join(module.__doc__.strip().split('\n')[2:])
            # input_lines = [f'.. rubric:: {module_title}', '   :class: module', module_doc, '']
        input_lines = ['']
        for name in names:

            # for klass in modules[module_name]:
            klass = get_normalizer(name)
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
                f':class:`{klass.__name__} <{klass.__module__}.{klass.__name__}>` class.'
            ])

        raw_text = '\n'.join(input_lines)
        include_lines = docutils.statemachine.string2lines(
            raw_text, tab_width, convert_whitespace=True)
        self.state_machine.insert_input(include_lines, '')

        return []


def doc_summary(lines):
    """Extract summary of docs."""
    summary = []
    for line in lines:
        stripped = line.strip().lower()
        if (stripped.startswith('to use this normalizer') or
                stripped.startswith('use ``method')):
            continue
        if (line.startswith('Parameters') or line.startswith('Example')
                or line.startswith('.. note::')):
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
