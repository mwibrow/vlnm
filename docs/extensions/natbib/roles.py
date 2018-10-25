"""
    New Roles
    ~~~~~~~~~~~~~~~~~~~~~~
    .. autoclass:: CitationRole
    .. autofunction:: extract_citation
"""

import re

from sphinx.errors import SphinxError

from .nodes import CitationNode

def extract_citation(rawtext):
    """
    Extract citation elements from a raw citations string
    """
    tokens = re.split(r'\s*\{%\s*(.*?)\s*%\}\s*', rawtext)
    if len(tokens) == 3:
        pre_text, keys, post_text = tokens
    else:
        pre_text, keys, post_text = '', tokens[0], ''
    key_list = [key.strip() for key in keys.split(',')]
    return pre_text, key_list, post_text

class CitationRole(object):
    """
        Class for processing the :rst:role:`citep` :rst:role:`citet`
        and  :rst:role:`citealp`  roles.
    """
    def __call__(self, typ, rawtext, text, lineno, inliner,
                 options=None, content=None):

        options = options or {}
        content = content or []
        env = inliner.document.settings.env
        if not typ:
            typ = env.temp_data.get('default_role')
            if not typ:
                typ = env.config.default_role
            if not typ:
                raise SphinxError('cannot determine default role!')
        else:
            typ = typ.lower()
        if ':' not in typ:
            domain, role = '', typ  # type: unicode, unicode
            classes = ['xref', role]
        else:
            domain, role = typ.split(':', 1)
        classes = ['xref', domain, '%s-%s' % (domain, role)]

        tokens = re.split(r'{%\s*(.*?)\s*%}', text)
        if len(tokens) == 1:
            tokens = ['', tokens[0], '']

        for i in range(1, len(tokens), 2):
            tokens[i] = [token.strip() for token in tokens[i].split(',')
                         if token.strip()]
            env.bibkeys.add_keys(tokens[i], env.docname)

        pre_text, keys, post_text = extract_citation(text)
        env.bibkeys.add_keys(keys, env.docname)

        node = CitationNode(data=dict(
            typ=typ,
            domain=domain,
            docname=env.docname,
            classes=classes,
            text=text,
            rawtext=rawtext,
            tokens=tokens,
            pre_text=pre_text,
            keys=keys,
            post_text=post_text
        ))
        return [node], []
