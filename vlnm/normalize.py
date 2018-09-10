"""
Vowel normalizer module
"""
from future.utils import raise_from
import re

import pandas as pd

from vlnm.utils import (
    items_to_str
)


def check_columns(df, column_specs, column_alias, groups):
    """
    Check if required and choice columns are present in the dataframe.
    """
    columns = column_specs.get('required', [])
    if columns:
        check_required_columns(df, columns, column_specs)

    columns = column_specs.get('choice', [])
    for choices in columns:
        check_choice_columns(df, columns[choices], column_alias)
        if choices == 'formants':
            formants = columns[choices]
            for formant in formants:
                if not re.match(r'f\d', formant):
                    raise_from(ValueError(
                        'Formant `{formant}` is invalid. '
                        'Formants should be specified as `fn` '
                        'where n is a number.'.format(
                            formant=formant
                        )), None)
    if groups:
        check_group_columns(df, groups, column_alias)

def check_required_columns(df, columns, column_alias):
    """
    Check required columns are in the data frame.
    """
    for column in columns:
        alias = column_alias.get(column)
        if alias and alias not in df:
            raise_from(ValueError(
                'Required column `{column}` aliased to `{alias}`, '
                'but `{alias}` is not in the data frame'.format(
                    column=column,
                    alias=alias)),
                None)
        else:
            if not column in df:
                raise_from(ValueError(
                    'Required column `{column}` is not in the data frame, '
                    'and no mapping given'.format(column=column)), None)

def check_choice_columns(df, columns, column_alias):
    """
    Check at least one of a choice of columns is in the data frame.
    """
    columns_str = items_to_str(
        columns, junction='or', quote="`")
    defaults = [column for column in columns
                if column not in column_alias]
    mappings = [column_alias[column] for column in columns
                if column in column_alias]
    if defaults:
        if not mappings and not any(default in df for default in defaults):
            raise_from(ValueError(
                'Expected one of columns {columns_str} '
                'in data frame'.format(columns_str=columns_str)), None)
    elif not any(mapping in df for mapping in mappings):
        if mappings:
            column, mapping = [
                (column, mapping)
                for column, mapping in column_alias if not mapping in df][0]

            raise_from(ValueError(
                'Expected one of colums {columns_str} in data frame. '
                '`{column}` was mapped to `{mapping}`, '
                'but `{mapping}` is not in the data frame'.format(
                    columns_str=columns_str,
                    column=column,
                    mapping=mapping
                )), None)
        raise_from(ValueError(
            'Expected one of columns {columns_str} '
            'in data frame'.format(columns_str=columns_str)), None)

def check_group_columns(df, groups, column_alias):
    """
    Check (aliased) group columns are in the data frame
    """
    for column in groups:
        alias = column_alias.get(column)
        if alias:
            if not alias in df:
                raise_from(ValueError(
                    'Grouping column `{column}` '
                    'aliased as `{alias}` not in data frame'.format(
                        column=column,
                        alias=alias
                    )), None)
        elif column not in df.columns:
            raise_from(ValueError(
                'Grouping column `{column}` not in data frame'.format(
                    column=column)), None)

def update_options(options, column_alias, column_specs):
    """Update options with column_alias keys (and vice versa).
    """
    for spec in column_specs:
        for column in column_specs[spec]:
            if column in options:
                column_alias[column] = options[column]
            else:
                if column in column_alias and column not in options:
                    options[column] = column_alias[column]
    return options, column_alias


class VowelNormalizer:
    """
    Base class for vowel normalizers.

    normalize(
        df,
        formants=['f1', 'f2', 'f3'],
        columns=dict(
            speaker: 'f3',
            f1='my_f1',
            f2='my_f2'
        )
    )
    """
    _column_specs = {}

    def __init__(self, **kwargs):
        self.default_kwargs = kwargs
        self.actions = {}

    def normalize(self, df, **kwargs):
        """Normalize the formant data in a data frame.

        """
        options = {}
        options.update(self.default_kwargs, **kwargs)

        column_alias = options.pop('column_alias', {})
        formants = options.pop('formants', [])
        groups = options.pop('groups', [])
        constants = options.pop('constants', {})
        actions = self.actions.update(options.pop('actions', {}))

        update_options(options, column_alias, self._column_specs)
        check_columns(
            df,
            self._column_specs,
            column_alias,
            groups)

        return self.partition(
            df,
            formants=formants,
            groups=groups,
            actions=actions,
            constants=constants,
            **options)

    def partition(self, df, **kwargs):
        """
        Partition the data frame for normalistion.
        """
        formants = kwargs.pop('formants')
        groups = kwargs.pop('groups')
        actions = kwargs.pop('actions')
        constants = kwargs.pop('constants')
        return self._partition(
            df,
            formants,
            groups,
            actions,
            constants,
            **kwargs)

    def _partition(
            self,
            df,
            formants,
            groups,
            actions,
            constants,
            **kwargs):

        if groups:
            group = groups[0]
            grouped = df.groupby(group, as_index=False)
            out_df = pd.DataFrame()
            for _, grouped_df in grouped:
                action = actions.get(group)
                if action:
                    action(
                        grouped_df,
                        constants,
                        **kwargs)
                normed_df = self._partition(
                    grouped_df.copy(),
                    formants,
                    groups[1:],
                    actions,
                    constants,
                    **kwargs)
                if normed_df is not None:
                    out_df = pd.concat([out_df, normed_df], axis=0)
            return out_df

        new_columns = kwargs.get('new_columns', '{}')
        normed_df = self.norm(
            df.copy() if new_columns else df,
            constants=constants,
            formants=formants,
            **kwargs)
        if new_columns:
            for formant in formants:
                df[new_columns.format(formant)] = normed_df[formant]
        return df

    def norm(self, df, **kwargs):  # pylint: disable=no-self-use,unused-argument
        """
        Default normalizer transform: do nothing.
        """

        return df


class FormantIntrinsicNormalizer(VowelNormalizer):
    r"""
    Base class for formant-intrinsic normaliztion.
    """

    def partition(self, df, **kwargs):
        """Override partition method from base class.
        """
        return self.norm(df, **kwargs)

    def norm(self, df, **kwargs):  # pylint: disable=arguments-differ
        column_alias = kwargs.pop('column_alias', {})
        new_columns = kwargs.pop('new_columns', '{}')
        formants = kwargs.pop('formants')
        columns_in = []
        columns_out = []
        for formant in formants:
            column = column_alias.get(formant, formant)
            columns_in.append(column)
            columns_out.append(new_columns.format(column))

        df[columns_out] = self.transform(df[columns_in])
        return df

    def transform(self, df, **_):  # pylint: disable=no-self-use
        """
        Default transform for formant intrinsic normalizers
        """
        return df
