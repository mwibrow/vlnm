"""
Misc. utilities.
"""

def quote_item(item, pre='', post=''):
    """Format an string item with quotes.
    """
    post = post or pre
    return f'{pre}{item}{post}'

def items_to_str(items, sep=',', junction=None, oxford=False, quote=None):
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
    elif len(items) == 1:
        return quote_item(sorted_items[0], quote)
    return '{}{} {}'.format(
        quote_item(sorted_items[0], quote),
        sep,
        items_to_str(
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

REQUIRED_COLUMN_NOT_FOUND = (
    'Required column \'{}\' not found in the data frame')
REQUIRED_COLUMN_GIVEN_NOT_FOUND = (
    'Required {} column (given as \'{}\') missing in data frame')
COLUMN_GIVEN_NOT_FOUND = (
    '{} column (given as \'{}\') missing in data frame')
AT_LEAST_ONE_COLUMN_NOT_FOUND = (
    'Expected at least one column from \'{}\' to be in data frame')
COLUMN_NOT_FOUND = (
    'Column \'{}\' missing in data frame')

def check_columns(df, column_specs, kwargs):
    """
    Check if required, optional and grouping columns are in the data frame.
    """
    for spec in column_specs:
        column = column_specs[spec]
        try:
            default = column
            given = kwargs.get(column, None)
            if not given and default not in df.columns:
                raise ValueError(
                    REQUIRED_COLUMN_NOT_FOUND.format(
                        default)) from None
            elif given is not None and given not in df.columns:
                raise ValueError(
                    REQUIRED_COLUMN_GIVEN_NOT_FOUND.format(
                        column, given)) from None
        except TypeError:
            givens = [kwargs.get(item) for item in column if kwargs.get(item)]
            if givens:
                for given in givens:
                    if not given in df.columns:
                        raise ValueError(
                            COLUMN_GIVEN_NOT_FOUND.format(
                                spec.capitalize(), given)) from None
            else:
                defaults = [item for item in column if not kwargs.get(item)]
                if not any(default in df.columns for default in defaults):
                    raise ValueError(
                        AT_LEAST_ONE_COLUMN_NOT_FOUND.format(
                            items_to_str(defaults))) from None
    if 'groups' in kwargs:
        for group in kwargs['groups']:
            if not group in df.columns:
                raise ValueError(
                    COLUMN_NOT_FOUND.format(group)) from None

def check_required_columns(column_specs, kwargs, replace=True):
    for spec in column_specs:
        column = column_specs[spec]
        try:
            if column not in kwargs:
                if replace:
                    kwargs[column] = column
                else:
                    raise ValueError()
        except TypeError:
            if not any(item in kwargs for item in column):
                if replace:
                    for item in column:
                        kwargs[item] = item
                else:
                    raise ValueError()
    return False




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

# def check_required_kwargs(kwargs, required):
#     """
#     Check required keyword arguments are present.
#     """
#     required = required or []
#     for key in required:
#         if not key in kwargs:
#             return key
#     return None

def check_one_from_kwargs(kwargs, one_from):
    """
    Check at least one-from keyword arguments is present.
    """
    for items in one_from:
        for item in items:
            if item in kwargs:
                break
        else:
            if one_from:
                return one_from
    return None

def check_data_frame_columns(df, columns):
    """
    Check data frame contains columns.
    """
    for column in columns:
        if not column in df.columns:
            return column
    return None
