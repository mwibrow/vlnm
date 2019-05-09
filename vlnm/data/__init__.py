"""
    Datasets
    ~~~~~~~~
"""

import enum
import os
from typing import Callable, Dict, List, Type, Union

import numpy as np
import pandas as pd

WHERE_AM_I = os.path.realpath(os.path.dirname(__file__))
USE_CACHE = False
CACHE = {}


class Dataset:
    """
    Base class for datasets.


    Parameters
    ----------

    source:
        Absolute file path to the dataset source.
        Must be readable by :func:`pd.read_csv`.

    dtypes:
        Dictionary mapping column names on
        data types (or functions that return data types).
    """

    def __init__(
            self,
            source: str,
            dtypes: Dict[str, Union[Callable, Type]] = None,
            **kwargs):
        self.source = source
        self.dtypes = dtypes or {}
        self.kwargs = kwargs

    def load(self, columns: List[str] = None, dtypes: bool = True):
        if USE_CACHE:
            if self.source not in CACHE:
                CACHE[self.source] = pd.read_csv(self.source, **self.kwargs)
            df = CACHE[self.source]
            if columns:
                df = df[columns]
        else:
            df = pd.read_csv(self.source, usecols=columns, **self.kwargs)
        dtypes = self.dtypes if dtypes else {}
        if dtypes:
            for column in df.columns:
                if column in self.dtypes:
                    try:
                        dtype = self.dtypes[column]
                        df[column] = dtype[0](df[column], dtype=dtype[1])
                    except IndexError:
                        df[column] = dtype(df[column])
        return df

    def __call__(self, **kwargs):
        return self.load(**kwargs)


def cache(enable: bool = True):
    """Enable caching for datasets.

    Parameters
    ----------
    enable:
        If ``True`` enable (or reset) the cache.
    """
    global CACHE, USE_CACHE  # pylint: disable=global-statement
    CACHE = {}
    USE_CACHE = enable


def categorical(series: pd.Series, dtype=str):
    return pd.Categorical(series.astype(dtype))


def pb1952(columns: List[str] = None, dtypes: bool = False) -> pd.DataFrame:
    """
    Return data derived from :citet:`peterson_barney_1952`.

    Parameters
    ----------

    columns:
        Specify which columns to return.
        If omitted all columns are returned.
    dtypes:
        By default, the data types
        for the columns
        will be automatically set
        (including wi)

    Returns
    -------
    :
        A Dataframe containing the data


    Dataset
    -------

    type: :class:`pandas.Categorical` of :class:`str`
        Type
    sex: :class:`pandas.Categorical` of :class:`str`
        Reported gender of speaker
    speaker: :class:`pandas.Categorical` of :class:`int`
        Speaker identifier
    vowel: :class:`pandas.Categorical` of :class:`str`
        Vowel label
    IPA: :class:`pandas.Categorical` of :class:`str`
        IPA symbol.
    f0 - f3: :class:`numpy.int64`
        Formant data in Hz.


    Examples
    --------

    .. ipython::

        from vlnm.data import pb1952

        pb1952(['speaker', 'vowel', 'f1', 'f2']).head()

    """
    return Dataset(
        os.path.join(WHERE_AM_I, 'pb1952.csv'),
        {
            'type': (pd.Categorical, str),
            'sex': categorical,
            'speaker': categorical,
            'vowel': categorical,
            'IPA': categorical,
            'f0': np.int64,
            'f1': np.int64,
            'f2': np.int64,
            'f3': np.int64
        })(columns=columns, dtypes=dtypes)
