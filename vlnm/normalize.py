"""
Vowel normalizer module
"""
import pandas as pd

import vlnm.decorators as decorators
from vlnm.utils import (
    check_columns,
    merge_columns
)

class VowelNormalizer:
    """
    Base class for vowel normalizers.
    """
    _column_specs = {}

    def __init__(self, **kwargs):
        self.default_kwargs = kwargs


    def normalize(self, df, **kwargs):
        """Normalize the formant data in a data frame.

        """
        current_kwargs = {}
        current_kwargs.update(self.default_kwargs, kwargs)
        source_map = check_columns(df, self._column_specs, current_kwargs)
        column_format = kwargs.get('new_columns', '{}')
        target_map = {key: column_format(key) for key in source_map}
        column_map = dict(
            source=source_map,
            target=target_map)

    def partition(
            self,
            df,
            groups,
            actions,
            column_map,
            constants,
            *args,
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
                        column_map,
                        *args,
                        **kwargs)
                normed_df = self.partition(
                    grouped_df,
                    groups[1:],
                    actions,
                    constants,
                    column_map,
                    *args,
                    **kwargs)
                if normed_df is not None:
                    out_df = pd.concat([out_df, normed_df], axis=0)
            return out_df
        if action:
            return self._normalize(df, constants, column_map, *args, **kwargs)
        return df

        def _normalize(
                self,
                df,
                constants,
                column_map,
                *args,
                **kwargs):  # pylint: disable=no-self-use,unused-argument
            """
            Default normalizer: do nothing.
            """
            return df
