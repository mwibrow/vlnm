"""
IPA extension for phontic base stuff
"""
from docutils import io, nodes, statemachine, utils
from docutils.parsers.rst.roles import math_role


def ipa_role(
        typ, rawtext, text, lineno, inliner,  # pylint: disable=unused-argument
        options=None, content=None):  # pylint: disable=unused-argument
    """
    Role for small caps.
    """
    if text.startswith('/') and text.endswith('/'):
        text = '/\u200A{}\u2006/'.format(text[1:-1])
    if r'^\prime' in rawtext:
        rawtext = rawtext[6:-1]
        parts = rawtext.split(r'^\prime')
        node = None
        for i, part in enumerate(parts):
            if part:
                if node:
                    node += nodes.inline(part, part, classes=['ipa'])
                else:
                    node = nodes.inline(part, part, classes=['ipa'])
            if i < len(parts) - 1:
                node += nodes.math(r'^\prime', r'^\prime')
        return [node], []

    text = r'\mathstrut\mbox{' + text + r'}'
    return [nodes.math(text, text, )], []


def f_role(
        typ, rawtext, text, lineno, inliner,  # pylint: disable=unused-argument
        options=None, content=None):  # pylint: disable=unused-argument
    """
    Role for formants caps.
    """
    text = 'F_{}'.format(text)
    return [nodes.math(text, text)], []


def setup(app):
    """
    Set up the sphinx extension.
    """
    app.add_role('f', f_role)
    app.add_role('ipa', ipa_role)
