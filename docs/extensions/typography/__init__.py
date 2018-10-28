"""
Console directive.
"""

import docutils.nodes


def tt_role(_typ, _rawtext, text, _lineno, _inliner, _options=None, _content=None):
    """Role for monospace text."""
    node = docutils.nodes.inline(text, text, classes=['tt'])
    return [node], []



def setup(app):
    """
    Set up the sphinx extension.
    """
    app.add_role('tt', tt_role)
