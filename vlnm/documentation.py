"""
Module for generating docstrings
"""
# pylint: disable=protected-access, invalid-name, too-few-public-methods


def document_columns(columns):  ## pylint: disable=unused-argument
    """
    Generate
    """
    docs = '''

    Args:
        foo (int): an integer
    Keyword:
        rename (string):
            A string which will be used to format the output columns.

    '''

    return docs.strip()

def document_keywords(name, keywords):
    """
    Generate keyword documentation.
    """
    docstring = '''
    {} {}
    '''.format(name, keywords)
    return docstring[-1:]
