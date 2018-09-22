"""
Vowel normalizer module
"""

import pandas as pd

from vlnm.validation import (
    Parameters,
    validate_columns,
    validate_keywords)

def prepare_df(df, columns, aliases):
    """
    Prepare
    """
    for column in columns:
        alias = aliases.get(column)
        if alias and alias in df:
            df[column] = df[alias]
    return df

FORMANTS = ['f0', 'f1', 'f2', 'f3']

class VowelNormalizer:
    """
    Base class for vowel normalizers.
    """
    _columns = Parameters()
    _keywords = Parameters()
    _name = ''
    _returns = []

    def __init__(self, **kwargs):
        self.default_kwargs = kwargs
        self.actions = {}
        self.groups = kwargs.pop('groups', [])

    def validate(self, df, aliases, **options):
        """
        Validate the arguments given to the normalize method.
        """
        validate_columns(
            self._name or self.__class__.__name__,
            df,
            self._columns,
            aliases,
            **options)

        validate_keywords(
            self._name or self.__class__.__name__,
            self._keywords,
            options)

    def normalize(self, df, **kwargs):
        """
        Normalize the formant data in a data frame.
        """
        options = {}
        options.update(self.default_kwargs, **kwargs)

        formants = options.pop('formants', [])
        if not formants:
            formants = [kwargs.get(formant) for formant in FORMANTS
                        if formant in kwargs]
        if not formants:
            formants = [formant for formant in FORMANTS if formant in df]
        aliases = options.pop('aliases', {})
        columns = (set(self._columns.as_list() + FORMANTS)
                   if self._columns else FORMANTS)
        for column in columns:
            alias = kwargs.pop(column, None)
            if alias:
                aliases[column] = alias

        groups = options.pop('groups', [])
        groups.extend(self.groups)
        constants = options.pop('constants', {})
        actions = options.pop('actions', {})
        actions.update(self.actions)

        self.validate(df, aliases, **options)

        return self.partition(
            df,
            formants=formants,
            groups=groups,
            actions=actions,
            constants=constants,
            aliases=aliases,
            **options)

    def partition(self, df, **kwargs):
        """
        Partition the data frame for normalistion.
        """
        formants = kwargs.pop('formants')
        groups = kwargs.pop('groups')
        actions = kwargs.pop('actions')
        constants = kwargs.pop('constants')
        aliases = kwargs.pop('aliases')
        return self._partition(
            df,
            formants,
            groups,
            actions,
            constants,
            aliases,
            **kwargs)

    def _partition(
            self,
            df,
            formants,
            groups,
            actions,
            constants,
            aliases,
            **kwargs):

        if groups:
            group = groups[0]
            grouped = df.groupby(group, as_index=False)
            out_df = pd.DataFrame()
            for _, grouped_df in grouped:
                action = actions.get(group)
                if action:
                    group_df = prepare_df(
                        grouped_df.copy(),
                        formants + groups,
                        aliases)
                    action(
                        group_df,
                        formants=formants,
                        constants=constants,
                        **kwargs)
                normed_df = self._partition(
                    grouped_df.copy(),
                    formants,
                    groups[1:],
                    actions,
                    constants,
                    aliases,
                    **kwargs)
                if normed_df is not None:
                    out_df = pd.concat([out_df, normed_df], axis=0)
            return out_df

        rename = kwargs.get('rename')
        group_df = prepare_df(
            df.copy(),
            formants + groups,
            aliases)

        normed_df = self.norm(
            group_df,
            formants=formants,
            constants=constants,
            aliases=aliases,
            **kwargs)

        returns = self._returns or formants
        rename = kwargs.get('rename')
        if rename:
            for column in returns:
                if column in normed_df:
                    df[rename.format(column)] = normed_df[column]
        else:
            for column in returns:
                if column in normed_df:
                    df[column] = normed_df[column]

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
        return self.pre_norm(df, **kwargs)

    def pre_norm(self, df, **kwargs):
        """
        Pre-normalization step.
        """

        aliases = kwargs.pop('aliases', {})
        rename = kwargs.pop('rename', None)
        formants = kwargs.get('formants', [])

        group_df = df.copy()
        group_df = prepare_df(group_df, formants, aliases)
        normed_df = self.norm(group_df, **kwargs)

        returns = self._returns or formants
        if rename:
            for column in returns:
                if column in normed_df:
                    df[rename.format(column)] = normed_df[column]
        else:
            for column in returns:
                if column in normed_df:
                    df[column] = normed_df[column]

        return df

    def norm(self, df, **_):  # pylint: disable=no-self-use
        """
        Default transform for formant intrinsic normalizers
        """
        return df
