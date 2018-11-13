"""
IPA extension for phontic base stuff
"""
from docutils import io, nodes, statemachine, utils
from docutils.parsers.rst.roles import math_role

def ipa_role(
        typ, rawtext, text, lineno, inliner, # pylint: disable=unused-argument
        options=None, content=None): # pylint: disable=unused-argument
    """
    Role for small caps.
    """
    if text.startswith('/') and text.endswith('/'):
        text = '/\u200A{}\u2006/'.format(text[1:-1])
    return [nodes.inline(text, text, classes=['ipa'])], []

def f_role(
        typ, rawtext, text, lineno, inliner, # pylint: disable=unused-argument
        options=None, content=None): # pylint: disable=unused-argument
    """
    Role for small caps.
    """
    text = 'F_{}'.format(text)
    return [nodes.math(text, text)], []

def setup(app):
    """
    Set up the sphinx extension.
    """
    app.add_role('f', f_role)
    app.add_role('ipa', ipa_role)
