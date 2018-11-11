"""
Misc. utilities.
"""

FORMANTS = ['f0', 'f1', 'f2', 'f3']

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


def get_formants_spec(**kwargs):
    """Sanitize the user formant specification for normalizers."""
    if any(kwargs.get(f) for f in FORMANTS):
        fmap = {f:kwargs.get(f)
                  if isinstance(kwargs.get(f), list) else [kwargs.get(f)]
                for f in FORMANTS}
        formants = []
        for f in fmap:
            if fmap[f][0]:
                formants.extend(fmap[f])
        flen = max(len(f) for f in fmap.values())
        for f in fmap:
            fmap[f].extend(fmap[f][-1:] * (flen - len(fmap[f])))
        spec = dict(**fmap)
        spec['formants'] = formants
        return spec
    if kwargs.get('formants'):
        return dict(
            f0=[None], f1=[None], f2=[None], f3=[None],
            formants=kwargs['formants'])
    return dict(
        f0=['f0'],
        f1=['f1'],
        f2=['f2'],
        f3=['f3'],
        formants=FORMANTS)
