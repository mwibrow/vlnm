"""
Class decorators for normalizers.
"""
# pylint: disable=protected-access, invalid-name, too-few-public-methods
from future.utils import raise_from

def DocString(cls):
    """
    Decorator for auto generating docstrings
    """
    return cls

class Parameters:
    """
    Base class for normalizer decorator.
    """
    def __init__(
            self,
            required=None,
            optional=None,
            choice=None):

        self.required = required
        self.choice = choice
        self.optional = optional

def Columns(**columns):
    """
    Decorator for specifying require and optional data frame columns.
    """
    def cls_decorator(cls):
        """
        Decorate {cls} with {_columns}
        """
        cls._columns = Parameters(**columns)
        return cls
    return cls_decorator

def Keywords(**keywords):
    """
    Decorator for specifying required and optional normalizer keywords.
    """
    def cls_decorator(cls):
        """
        Decorate {cls} with {_keywords}
        """
        cls._keywords = Parameters(**keywords)
        return cls
    return cls_decorator

def Returns(**returns):
    """
    Decorator for specifying columns returned by a normalizer.
    """

    def cls_decorator(cls):
        """
        Decorate {cls} with {_returns}
        """
        cls._returns = returns

def validate_columns(df, columns, aliases, errors=True):
    """
    Validate columns against a data frame.
    """
    if columns.required:
        validate_required_columns(df, columns.required, aliases)
    if columns.choice:
        validate_choice_columns(df, columns.choice, aliases)
    return True

def validate_required_columns(df, columns, aliases):
    """
    Validate required columns against a data frame.
    """
    for name in columns:
        column = aliases.get(name, name)
        if column in df:
            continue
        if column in aliases:
            raise_from(ValueError(
                'Required column {name} was aliased to {column}. '
                'But {column} is not in the data frame.'.format(
                    name=name,
                    column=column)
            ), None)
        raise_from(ValueError(
            'Required column {name} is not in the data frame.'.format(
                name=name)), None)
    return True

def validate_choice_columns(df, columns, aliases):
    """
    Validate choice columns against a data frame.
    """
    missing = [name for name in columns
        if name not in aliases and aliases.get(name, name) not in df]
    if any(missing):
        name = missing[0]
        column_list = columns
        if name in aliases:
            column = aliases
            raise_from(ValueError(
                'Expected one of {column_list} to be in the data frame. '
                '{name} was was aliased to {column}. '
                'But {column} is not in the data frame.'.format(
                    column_list=column_list,
                    name=name,
                    column=column)
            ), None)
        raise_from(ValueError(
            'Expected one of {column_list} to be in the data frame. '.format(
                 columns_list=column_list), None))

def validate_keywords(expected, actual):
    """
    Validate keyword arguments.
    """
    if keywords.required:
        validate_required_keywords(expected, actual)
    if keywords.required:
        validate_required_keywords(expected, actual)