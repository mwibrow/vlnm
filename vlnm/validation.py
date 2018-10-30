"""
Module for validating normalizer columns and arguments.
"""
# pylint: disable=invalid-name, protected-access, too-few-public-methods

from future.utils import raise_from

from vlnm.utils import nameify

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
    Exception raised when a choice alised column is missing.
    """


class RequiredKeywordMissingError(Exception):
    """
    Exception raisd when a required keyword is missing.
    """


class ChoiceKeywordMissingError(Exception):
    """
    Exception raised when a choice keyword is missing.
    """


class GroupsContainRequiredColumnError(Exception):
    """
    Exception raised when a required column is in the groups specification.
    """


class GroupsContainChoiceColumnError(Exception):
    """
    Exception raised when a choice column is in the groups specification.
    """

def validate_columns(normalizer, df, columns, aliases, **kwargs):
    """
    Validate columns against a data frame.
    """
    if columns.required:
        validate_required_columns(
            normalizer, df, columns.required, aliases, **kwargs)
    if columns.choice:
        validate_choice_columns(
            normalizer, df, columns.choice, aliases)
    return True

def validate_required_columns(normalizer, df, columns, aliases, **kwargs):
    """
    Validate required columns against a data frame.
    """
    for name in columns:
        column = kwargs.get(name) or aliases.get(name) or name
        if column in df:
            continue
        if name in aliases:
            raise_from(RequiredColumnAliasMissingError(
                '{normalizer} requires column {name}. '
                'The column {name} was aliased to {column}. '
                'But {column} is not in the data frame.'.format(
                    normalizer=normalizer,
                    name=nameify([name], quote='\''),
                    column=nameify([column], quote='\''))
            ), None)
        raise_from(RequiredColumnMissingError(
            ' {normalizer} requires column {name}. '
            'But {name} is not in the data frame.'.format(
                normalizer=normalizer,
                name=nameify([name], quote='\'')
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
                    'The column {name} was was aliased to {column}. '
                    'But {column} is not in the data frame.'.format(
                        normalizer=normalizer,
                        column_list=nameify(columns, junction='or', quote='\''),
                        name=nameify([name], quote='\''),
                        column=nameify([column], quote='\''))
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
            '{normalizer} required {keyword} keyword argument'.format(
                normalizer=normalizer,
                keyword=nameify([keyword])
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
                '{normalizer} expected one of {keywords} '
                'as a keyword argument'.format(
                    normalizer=normalizer,
                    keywords=nameify(keywords, junction='or', quote='\'')
                    )), None)
    return True

def validate_groups(required, choice, groups, aliases):
    """
    Check required and choice columns are not in the groups.
    """
    required = required or []
    choice = choice or []
    for column in required:
        if aliases.get(column, column) in groups:
            raise_from(GroupsContainRequiredColumnError(
                'Required column {column} was specified as a '
                'grouping column'.format(
                    column=column)), None)
    for choices in choice:
        for column in choice[choices]:
            if aliases.get(column, column) in groups:
                raise_from(GroupsContainChoiceColumnError(
                    'Choice column {column} was specified as a '
                    'grouping column'.format(
                        column=column)), None)
