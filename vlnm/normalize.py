"""
Vowel normalizer module
"""
import pandas as pd

import vlnm.decorators as decorators


def check_columns(df, column_specs, groups):
    for spec in column_specs:
        if spec == 'required':
            for column in column_specs[spec]:
                if not column in df.columns:
                    raise ValueError()
        else:
            if not any(column in df for column in column_specs[spec]):
                raise ValueError()
    for column in groups:
        if not column in df.columns:
            raise ValueError()

class VowelNormalizer:
    """
    Base class for vowel normalizers.
    """
    _column_specs = {}

    def __init__(self, **kwargs):
        self.default_kwargs = kwargs
        self.actions = {}

    def normalize(self, df, **kwargs):
        """Normalize the formant data in a data frame.

        """
        current_kwargs = {}
        current_kwargs.update(self.default_kwargs, kwargs)

        groups = current_kwargs.get('groups') or []
        check_columns(df, self._column_specs, groups)
        self.partition(df, groups, {}, **kwargs)

    def partition(
            self,
            df,
            groups,
            actions,
            constants,
            new_columns=column_format,
            **kwargs):
        """
        Partition the data frame for normalistion.
        """

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
                normed_df = self.partition(
                    grouped_df.copy(),
                    groups[1:],
                    actions,
                    constants,
                    **kwargs)
                if normed_df is not None:
                    out_df = pd.concat([out_df, normed_df], axis=0)
            return out_df

        out_df = self._normalize(
            df.copy() if new_columns else df,
            constants,
            **kwargs)
        if new_columns:
            for column in ['f0', 'f1', 'f2', 'f3']:
                if column in out_df.columns:
                    df[new_column.format(column)] = out_df[column]
            return df
        return out_df

        return df

    def _normalize(
            self,
            df,
            constants,
            **kwargs):  # pylint: disable=no-self-use,unused-argument
        """
        Default normalizer: do nothing.
        """
        return df

class FormantIntrinsicNormalizer(VowelNormalizer):
    r"""
    Base class for formant-intrinsic normaliztion.
    """

    required = ['formants']

    def _normalize_df(self, df, columns_map, **__):
        df[cols_in] = df[cols_out]
        return df

    def normalize(self, df, **kwargs):
        """
        Normalize the a data frame.

        Paramters
        ---------
        df: pandas.DataFrame
        """
        return self._normalize(
            df,
            margins=[],
            callbacks=[self._normalize_df],
            **kwargs)

class Log10Normalizer(FormantIntrinsicNormalizer):
    r"""
    Normalize using the base 10 logarithm of the formant values.

     .. math::

       F_i^N = \log_{10}\left(F_i\right)
    """
    def _normalize_df(self, df, cols_in, cols_out, **__):
        """
        Normalize using log10
        """
        df[cols_out] = np.log10(df[cols_in])
        return df