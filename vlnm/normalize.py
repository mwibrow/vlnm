"""
Vowel normalizer module
"""
import pandas as pd

import vlnm.decorators as decorators


def check_columns(df, column_specs, column_map, groups):
    for spec in column_specs:
        if spec == 'required':
            for column in column_specs[spec]:
                if column in column_map and column[column] not in df:
                    raise ValueError('required column A mapped to B but B not in dataframe')
                if not column in df:
                    raise ValueError('required column A not it dataframe and no mapping given')
        else:
            defaults = [column for column in column_specs[spec]
                        if column not in column_map]
            mappings = [column_map[column] for column in column_specs[spec]
                        if column in column_map]
            if defaults:
                if not mappings and not any(default in df for default in defaults):
                    raise ValueError('expected one of A columns in dataframe')
            else:
                if not any(mapping in df for mapping in mappings):
                    if mappings:
                        column, mapping = [(column, mapping)
                            for column, mapping in column_map if not mapping in df][0]
                        raise ValueError('expected one of A colums in dataframe'
                            'B was mapped to C but C is not in dataframe')
                    else:
                        raise ValueError('expected one of A columns in dataframe.')

    for column in groups:
        if not column in df.columns:
            raise ValueError()

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
        options.update(self.default_kwargs, kwargs)

        column_map = options.pop('columns', {})
        formants = options.pop('formants', [])
        groups = options.pop('groups', [])
        constants = options.pop('constats', {})
        actions = self.actions
        check_columns(
            df,
            self._column_specs,
            column_map,
            groups)

        for formant in formants:
            options[formant] = (
                options.get(formant) or
                column_map.get(formant) or
                formant)

        return self.partition(
            df,
            formants,
            groups,
            actions,
            constants,
            **options)

    def partition(
            self,
            df,
            formants,
            groups,
            actions,
            constants,
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
                    formants,
                    groups[1:],
                    actions,
                    constants,
                    **kwargs)
                if normed_df is not None:
                    out_df = pd.concat([out_df, normed_df], axis=0)
            return out_df

        new_columns = kwargs['new_columns']
        normed_df = self._normalize(
            df.copy() if new_columns else df,
            constants,
            **kwargs)
        if new_columns:
            for formant in formants:
                df[new_columns.format(formant)] = normed_df[formant]
        return df

    def _normalize(
            self,
            df,
            formants,
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