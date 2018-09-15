"""
Vowel normalizer module
"""

import pandas as pd

from vlnm.validation import (
    validate_columns,
    validate_keywords)

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
        aliases = kwargs.pop('aliases', {})
        new_columns = kwargs.pop('new_columns', '{}')
        formants = kwargs.pop('formants')
        columns_in = []
        columns_out = []
        for formant in formants:
            column = aliases.get(formant, formant)
            columns_in.append(column)
            columns_out.append(new_columns.format(column))

        df[columns_out] = self.transform(df[columns_in])
        return df

    def transform(self, df, **_):  # pylint: disable=no-self-use
        """
        Default transform for formant intrinsic normalizers
        """
        return df
