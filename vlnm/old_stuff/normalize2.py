"""
Module for vowel normalization


Normalizer(
    df,
    groups=['test', 'variabilty'],
    columns=dict(
        speaker='particiant',
        f0='f0',
        f1='f1',
        f2='f2',
        f3='f3')
)
"""

import numpy as np
import pandas as pd

from .decorators import (
    columns as Columns,
    docs as Docs
)
from .utils import (
    merge_columns,
    str_or_list)


@Docs
@Columns(
    required='speaker',
    formants=['f0', 'f1', 'f2', 'f3']
)
class Normalizer:
    """
    Base class for normalizers

    vowel_normalizer.normalize(
        df,
        columns=dict(
            formants=dict(
                f0='F0',
                f1='F1'
            )
        )
    )
    """
    _columns = {}

    def __init__(self, **kwargs):
        self.default_kwargs = merge_columns(self._columns, kwargs)

    def normalize(self, df, **kwargs):
        """
        Normalize a dataframe.
        """
        normalizer_kwargs = {}
        normalizer_kwargs.update(self.default_kwargs, kwargs)
        normalizer_kwargs = merge_columns(self._columns, kwargs)

    def partition(
            self,
            df,
            margins,
            actions,
            column_map,
            constants,
            *args,
            **kwargs):
        """
        Partition the data frame for normalistion.
        """

        if margins:
            margin = margins[0]
            groups = df.groupby(margins, as_index=False)
            out_df = pd.DataFrame()
            for _, group_df in groups:
                action = actions.get(margin)
                if action:
                    action(
                        group_df,
                        constants,
                        column_map,
                        *args,
                        **kwargs)
                normed_df = self.partition(
                    group_df,
                    margins[1:],
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
            **kwargs): # pylint: disable=no-self-use,unused-argument
        """
        Default normalization
        """
        return df



class VowelNormalizer(object):
    """
    The VowelNormalizer class is the base class for all normalizers.
    """
    required = []
    one_from = []

    def partition(
            self,
            df,
            margins,
            callbacks,
            columns_in,
            columns_out=None,
            constants=None,
            **kwargs):
        """
        Normalize a data frame.

        The data frame is recursively partitioned and at each
        level of recursion, partitions are processed using callbacks.
        These callbacks can calculate partition-level constants
        which are passed to the next recustion level.
        """
        if not callbacks:
            return df
        columns_out = columns_out or columns_in
        constants = constants or {}
        remove_none = kwargs.get('remove_none')
        if not margins and callbacks:
            for cols_in, cols_out in zip(columns_in, columns_out):
                cols_in = str_or_list(cols_in)
                cols_out = str_or_list(cols_out)
                if remove_none:
                    cols_in = [col for col in cols_in if col]
                    cols_out = [col for col in cols_out if col]
                df = callbacks[0](
                    df,
                    cols_in=cols_in,
                    cols_out=cols_out,
                    constants=constants,
                    **kwargs)
            return df

        margin, callback = margins[0], callbacks[0]
        margin_df = pd.DataFrame()
        grouped = df.groupby(by=margin, as_index=False) if margin else df

        for _, group_df in grouped:
            processed_df = group_df.copy()
            if callback:
                for cols_in, cols_out in zip(columns_in, columns_out):
                    if remove_none:
                        cols_in = [col for col in cols_in if col]
                        cols_out = [col for col in cols_out if col]
                    processed_df = callback(
                        processed_df,
                        cols_in=cols_in,
                        cols_out=cols_out,
                        constants=constants,
                        **kwargs)
                    if len(callbacks) > 1:
                        processed_df = self.partition(
                            processed_df,
                            margins[1:],
                            callbacks[1:],
                            cols_in,
                            cols_out,
                            constants,
                            **kwargs)
            margin_df = pd.concat([
                margin_df,
                processed_df
            ])
        return margin_df

    def _normalize(self, df, **kwargs):
        """
        Return normalize the formants in dataframe.
        """
        missing = check_required_kwargs(kwargs, self.required)
        if missing:
            raise ValueError(
                '{} requires keyword argument {}'.format(
                    self.__class__.__name__,
                    missing))
        missing = check_one_from_kwargs(kwargs, self.one_from)
        if missing:
            raise ValueError(
                '{} requires one keyword argument from {}'.format(
                    self.__class__.__name__,
                    missing))

        formants = sanitize_formants(kwargs.pop('formants'))

        columns_in, columns_out = get_columns_out(
            formants,
            kwargs.pop('suffix', {}))
        return self.partition(
            df,
            kwargs.pop('margins', []),
            kwargs.pop('callbacks', []),
            columns_in,
            columns_out,
            kwargs.pop('constants', {}),
            **kwargs)


def sanitize_formants(formants=None, f0=None, f1=None, f2=None, f3=None, **_):
    """
    Internal function for sanitizing formant arguments.

    Parameters
    ----------
    {}
    """.format(
        FORMANT_KWARGS_DOCSTRING
    )
    if formants is None:
        formants = [f0, f1, f2, f3]
    if isinstance(formants, list):
        formants = [str_or_list(formant) for formant in formants]
    else:
        formants = [str_or_list(formants.get(key))
                    for key in ['f0', 'f1', 'f2', 'f3']]

    max_len = max(len(formant) for formant in formants)
    formants = [formant + formant[-1:] * (max_len - len(formant))
                for formant in formants]
    formants = [[formants[i][j] for i in range(len(formants))]
                for j in range(max_len)]
    return formants


def get_columns_out(columns_in, suffix=None):
    """
    Return the 'out' columns givin the 'in' columns.
    """
    if not columns_in or not suffix:
        return columns_in, columns_in
    transform = np.vectorize(lambda value: '{}{}'.format(value, suffix) if value else value)
    # columns_out = ['{}{}'.format(value, suffix) if value else value
    #                for value in columns_in]
    return columns_in, transform(columns_in).tolist()


FORMANT_KWARGS_DOCSTRING = """
    formants: list[str] or dict
        A list of the columns that contain formant data.
    f0: str / list[str]
        alternative key for specifying the column for F0 data.
    f1: str / list[str]
        Alternative key for specifying the column for F1 data.
    f2: str / list[str]
        Alternative key for specifying the column for F2 data.
    f3: str / list[str]
        Alternative key for specifying the column for F3 data.
"""

COMMON_KWARGS_DOCSTRING = """
    speaker: str
        Name of the column which contains the speaker labels.
    vowel: str
        Name of the column which contains the vowel labels.
    gender: str
        Name of the column which contains gender labels.
    female: str
        Name of the label corresponding to individuals identified/identifying as female.
    male: str
        Name of the label corresponding to individuals identified/identifying as male.
    margins: list[str]
        Other columns to group the data over.
    suffix: str
        By default, formant columns are replaced by their normalized
        values; Specifying a suffix will add new columns,
"""
