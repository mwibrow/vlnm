"""
Vowel normalizer module
"""

import pandas as pd

from vlnm.validation import (
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

class VowelNormalizer:
    """
    Base class for vowel normalizers.
    """
    _columns = None
    _keywords = None
    _name = None
    _returns = None

    def __init__(self, **kwargs):
        self.default_kwargs = kwargs
        self.default_kwargs.update(
            f0='f0',
            f1='f1',
            f2='f2',
            f3='f3')
        self.actions = {}

    def normalize(self, df, **kwargs):
        """Normalize the formant data in a data frame.

        """
        options = {}
        options.update(self.default_kwargs, **kwargs)

        aliases = options.pop('aliases', {})
        formants = options.pop('formants', [])
        groups = options.pop('groups', [])
        constants = options.pop('constants', {})
        actions = self.actions.update(options.pop('actions', {}))

        validate_columns(
            self._name or self.__class__.__name__,
            df,
            self._columns,
            aliases)

        validate_keywords(
            self._name or self.__class__.__name__,
            self._keywords,
            options)

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
                        constants,
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

        rename = kwargs.get('rename', '{}')
        group_df = prepare_df(
            df.copy(),
            formants + groups,
            aliases)

        normed_df = self.norm(
            group_df,
            constants=constants,
            **kwargs)

        rename = kwargs.get('rename')
        if rename:
            for column in normed_df.columns:
                df[rename.format(column)] = normed_df[column]
        else:
            for column in normed_df.columns:
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
        return self.norm(df, **kwargs)

    def norm(self, df, **kwargs):  # pylint: disable=arguments-differ
        aliases = kwargs.pop('aliases', {})
        rename = kwargs.pop('rename', '{}')
        formants = kwargs.pop('formants')

        group_df = df.copy()
        group_df = prepare_df(group_df, formants, aliases)
        normed_df = self.transform(df, **kwargs)

        if rename:
            for column in normed_df.columns:
                df[rename.format(column)] = normed_df[column]
        else:
            for column in normed_df.columns:
                df[column] = normed_df[column]

        return df

    def transform(self, df, **_):  # pylint: disable=no-self-use
        """
        Default transform for formant intrinsic normalizers
        """
        return df
