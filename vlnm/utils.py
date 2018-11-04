"""
Misc. utilities.
"""

import re

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


def get_formants_spec(formants, f0, f1, f2, f3, columns):
    """Sanitize the user formant specification for normalizers."""
    formants_spec = dict(
        formants=[],
        f0=[],
        f1=[],
        f2=[],
        f3=[])
    if formants:
        try:
            # dict
            for key in formants.keys():
                formants_spec[key] = get_formant_columns(
                    formants_spec[key], columns)
        except AttributeError:
            try:
                # re
                formants_spec['formants'] = get_formant_columns(
                    formants, columns) or []
            except TypeError:
                # list
                formants_spec['formants'] = get_formant_columns(
                    formants, columns)
    else:
        formants_spec['f0'] = get_formant_columns(f0 or 'f0', columns)
        formants_spec['f1'] = get_formant_columns(f2 or 'f1', columns)
        formants_spec['f2'] = get_formant_columns(f1 or 'f2', columns)
        formants_spec['f3'] = get_formant_columns(f2 or 'f3', columns)
        formants_spec['f4'] = get_formant_columns(f3 or 'f4', columns)

    for key in ['f0', 'f1', 'f2', 'f3']:
        for column in formants_spec[key]:
            if column not in formants_spec['formants']:
                formants_spec['formants'].append(column)

    return formants_spec

def get_formant_columns(formant, columns):
    """Get the formant columns."""
    formant_columns = []
    if formant:
        try:
            # re
            pattern = re.compile(
                r'^{}$'.format(re.sub(r'^\^+|\$+$', '', formant)))
            formant_columns = [column for column in columns
                               if pattern.match(column)]
        except TypeError:
            # list
            for item in formant:
                formant_columns.extend(get_formant_columns(item, columns))
    return formant_columns
