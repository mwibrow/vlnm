"""
Module for validating normalizer columns and arguments.
"""

from future.utils import raise_from

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
                    name=name,
                    column=column)
            ), None)
        raise_from(RequiredColumnMissingError(
            ' {normalizer} requires column {name}. '
            'But {name} is not in the data frame.'.format(
                normalizer=normalizer,
                name=name
            )), None)
    return True

def validate_choice_columns(normalizer, df, choices, aliases):
    """
    Validate choice columns against a data frame.
    """
    for choice in choices:
        columns = choices[choice]
        missing = [name for name in columns
                   if name not in aliases and aliases.get(name, name) not in df]
        if any(missing):
            name = missing[0]
            column_list = columns
            if name in aliases:
                column = aliases
                raise_from(ChoiceColumnAliasMissingError(
                    '{normalizer} expected one of {column_list} '
                    'to be in the data frame. '
                    '{name} was was aliased to {column}. '
                    'But {column} is not in the data frame.'.format(
                        normalizer=normalizer,
                        column_list=column_list,
                        name=name,
                        column=column)
                ), None)
            raise_from(ChoiceColumnMissingError(
                '{normalizer} expected one of {column_list} '
                'to be in the data frame. '.format(
                    normalizer=normalizer,
                    column_list=column_list)
                ), None)

def validate_keywords(normalizer, expected, actual):
    """
    Validate keyword arguments.
    """
    if expected.required:
        validate_required_keywords(normalizer, expected, actual)
    if expected.choice:
        validate_choice_keywords(normalizer, expected, actual)
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
                keyword=keyword
                ), None))

def validate_choice_keywords(normalizer, expected, actual):
    """
    Validate choice keywords
    """
    present = [keyword for keyword in expected
               if keyword in actual]
    if not present:
        keywords = [keyword for keyword in expected]
        raise_from(ChoiceKeywordMissingError(
            '{normalizer} expected one of {keywords} argument'.format(
                normalizer=normalizer,
                keywords=keywords
                ), None))
