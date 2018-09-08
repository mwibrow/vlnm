"""
Vowel normalizer module
"""
import pandas as pd

from vlnm.utils import (
    items_to_str
)


def check_columns(df, column_specs, column_map, groups):
    """Check if required and given columns are present in the dataframe

    """
    # Check the column specificaton for the class.
    for spec in column_specs:
        if spec == 'required':
            # Required column.
            for column in column_specs[spec]:
                mapped_column = column_map.get(column)
                if mapped_column and mapped_column not in df:
                    raise ValueError(
                        f'Required column `{column}` mapped to `{mapped_column}`, '
                        f'but `{mapped_column}`` is not in the data frame')
                if not column in df:
                    raise ValueError(
                        f'Required column `{column}`` is not in the data frame, '
                        f'and no mapping given')
        else:
            # Optionally required columns (i.e., at least one)
            columns = column_specs[spec]
            columns_str = items_to_str(
                columns, junction='or', quote="`")
            defaults = [column for column in columns
                        if column not in column_map]
            mappings = [column_map[column] for column in columns
                        if column in column_map]
            if defaults:
                if not mappings and not any(default in df for default in defaults):
                    raise ValueError(
                        f'Expected one of columns {columns_str} in data frame')
            else:
                if not any(mapping in df for mapping in mappings):
                    if mappings:
                        column, mapping = [
                            (column, mapping)
                            for column, mapping in column_map if not mapping in df][0]

                        raise ValueError(
                            f'Expected one of colums {columns_str} in data frame. '
                            f'`{column}` was mapped to `{mapping}`, '
                            f'but `{mapping}` is not in the data frame')
                    else:
                        raise ValueError(
                            f'Expected one of columns {columns_str} in data frame')
    # Columns in groups
    for column in groups:
        if not column in df.columns:
            raise ValueError(
                f'Grouping column `{column}` not in data frame')


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

    def _transform(self, df):  # pylint: disable=no-self-use
        return df

    def partition(self, df, **kwargs):  # pylint: disable=arguments-differ
        """Override partition method from base class.
        """
        return self._normalize(df, **kwargs)

    def _normalize(self, df, **kwargs):  # pylint: disable=arguments-differ
        column_map = kwargs.pop('column_map', {})
        new_columns = kwargs.pop('new_columns', '{}')
        formants = kwargs.pop('formants')
        columns_in = []
        columns_out = []
        for formant in formants:
            column = column_map.get(formant, formant)
            columns_in.append(column)
            columns_out.append(new_columns.format(column))

        df[columns_out] = self._transform(df[columns_in])
        return df
