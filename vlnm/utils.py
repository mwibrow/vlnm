"""
Misc. utilities.
"""

def quote_item(item, pre='', post=''):
    """Format an string item with quotes.
    """
    post = post or pre
    return f'{pre}{item}{post}'

def nameify(items, sep=',', junction=None, oxford=False, quote=None):
    """
    Convert a list of items to a nicely formatted stringified list.
    """
    if not items:
        return ''
    sorted_items = sorted(items)
    quote = quote or ''
    if len(sorted_items) == 2:
        return ''.join([
            quote_item(sorted_items[0], quote),
            sep if oxford or not junction else '',
            ' {} '.format(junction) if junction else ' ',
            quote_item(sorted_items[1], quote)
        ])
    if len(items) == 1:
        return quote_item(sorted_items[0], quote)
    return '{}{} {}'.format(
        quote_item(sorted_items[0], quote),
        sep,
        nameify(
            sorted_items[1:],
            sep=sep,
            junction=junction,
            oxford=oxford,
            quote=quote))

def merge_columns(column_specs, kwargs):
    """
    Merge required columns with given columns
    """
    for spec in column_specs:
        column = column_specs[spec]
        try:
            if column not in kwargs:
                kwargs[column] = column
        except TypeError:
            if not any(item in kwargs for item in column):
                for item in column:
                    kwargs[item] = item
    return kwargs


def flatten(items):
    """
    Flatten a list of lists.
    """
    if items == []:
        return items
    if isinstance(items, list):
        flattend = []
        for item in items:
            flattend.extend(flatten(item))
        return flattend
    return [items]

def str_or_list(value):
    """
    String to list of string.
    """
    if isinstance(value, list):
        return value
    return [value]
