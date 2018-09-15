"""
Module for validating normalizer columns and arguments.
"""
# pylint: disable=protected-access, invalid-name, too-few-public-methods

from future.utils import raise_from

from vlnm.utils import nameify

class Parameters:
    """
    Base class for normalizer decorator.
    """
    def __init__(
            self,
            required=None,
            optional=None,
            choice=None,
            returns=None):

        self.required = required
        self.choice = choice
        self.optional = optional
        self.returns = returns

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

def Name(name):
    """
    Decorator for adding custom name to a normalizer class.
    """
    def cls_decorator(cls):
        """
        Decorate {cls} with {_name}
        """
        cls._name = name
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
    return cls_decorator

def Defaults(**defaults):
    """
    Decorator for specifying default columns/defaults
    """

    def cls_decorator(cls):
        """
        Decorate {cls} with {_defaults}
        """
        cls._defaults = defaults
    return cls_decorator

class RequiredColumnMissingError(Exception):
    """
    Exception raised when a required column is missing.
    """

class RequiredColumnAliasMissingError(Exception):
    """
    Exception raised when an aliased column is missing.
    """

class ChoiceColumnMissingError(Exception):
    """
    Exception raised when a choice column is missing.
    """

class ChoiceColumnAliasMissingError(Exception):
    """
    Exception raises when a choice alised column is missing.
    """

class RequiredKeywordMissingError(Exception):
    """
    Exception raise when a required keyword is missing.
    """

class ChoiceKeywordMissingError(Exception):
    """
    Exception raise when a choice column is missing.
    """

def validate_columns(normalizer, df, columns, aliases):
    """
    Validate columns against a data frame.
    """
    if columns.required:
        validate_required_columns(normalizer, df, columns.required, aliases)
    if columns.choice:
        validate_choice_columns(normalizer, df, columns.choice, aliases)
    return True

def validate_required_columns(normalizer, df, columns, aliases):
    """
    Validate required columns against a data frame.
    """
    for name in columns:
        column = aliases.get(name, name)
        if column in df:
            continue
        if name in aliases:
            raise_from(RequiredColumnAliasMissingError(
                '{normalizer} requires column {name}. '
                '{name} was aliased to {column}. '
                'But {column} is not in the data frame.'.format(
                    normalizer=normalizer,
                    name=nameify(name, quote='\''),
                    column=nameify(column, quote='\''))
            ), None)
        raise_from(RequiredColumnMissingError(
            ' {normalizer} requires column {name}. '
            'But {name} is not in the data frame.'.format(
                normalizer=normalizer,
                name=nameify(name, quote='\'')
            )), None)
    return True

def validate_choice_columns(normalizer, df, choices, aliases):
    """
    Validate choice columns against a data frame.
    """
    for choice in choices:
        columns = choices[choice]
        missing = [name for name in columns
                   if aliases.get(name, name) not in df]
        if len(missing) == len(columns):
            name = missing[0]
            if name in aliases:
                column = aliases
                raise_from(ChoiceColumnAliasMissingError(
                    '{normalizer} expected one of {column_list} '
                    'to be in the data frame. '
                    '{name} was was aliased to {column}. '
                    'But {column} is not in the data frame.'.format(
                        normalizer=normalizer,
                        column_list=nameify(columns, junction='or', quote='\''),
                        name=nameify(name, quote='\''),
                        column=nameify(column, quote='\''))
                ), None)
            raise_from(ChoiceColumnMissingError(
                '{normalizer} expected one of {column_list} '
                'to be in the data frame. '.format(
                    normalizer=normalizer,
                    column_list=nameify(columns, junction='or', quote='\''))
                ), None)

def validate_keywords(normalizer, expected, actual):
    """
    Validate keyword arguments.
    """
    if expected:
        if expected.required:
            validate_required_keywords(normalizer, expected.required, actual)
        if expected.choice:
            validate_choice_keywords(normalizer, expected.choice, actual)
    return True

def validate_required_keywords(normalizer, expected, actual):
    """
    Validate required keywords.
    """
    missing = [keyword for keyword in expected
               if not keyword in actual]
    if missing:
        keyword = missing[0]
        raise_from(RequiredKeywordMissingError(
            '{normalizer} required {keyword} argument'.format(
                normalizer=normalizer,
                keyword=nameify(keyword)
                )), None)
    return True

def validate_choice_keywords(normalizer, choices, actual):
    """
    Validate choice keywords
    """
    for choice in choices:
        keywords = choices[choice]
        present = [keyword for keyword in keywords
                   if keyword in actual]
        if not present:
            raise_from(ChoiceKeywordMissingError(
                '{normalizer} expected one of {keywords} argument'.format(
                    normalizer=normalizer,
                    keywords=nameify(keywords, junction='or', quote='\'')
                    )), None)
    return True
