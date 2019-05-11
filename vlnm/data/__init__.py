"""
    Datasets
    ~~~~~~~~

    |vlnm| distributes a small number of datasets
    containing formant data, which can be used to
    test or evaluate normalizers.

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
    r"""
    Base class for datasets.


    Parameters
    ----------

    source:
        Absolute file path to the dataset source.
        Must be readable by :func:`pd.read_csv`.

    dtypes:
        Dictionary mapping column names on
        data types.


    Other parameters
    ----------------

    \*\*kwargs:
        Passed on to the :func:`pd.read_csv` function
        when data is loaded.

    """

    def __init__(
            self,
            source: str,
            dtypes: Dict[str, Union[Callable, Type]] = None,
            **kwargs):
        self.source = source
        self.dtypes = dtypes or {}
        self.kwargs = kwargs

    def load(
            self,
            columns: List[str] = None,
            cast=True,
            dtypes: Dict[str, Union[Callable, Type]] = None,
            cache: bool = False):
        """
        Load a dataset from disk or the cache.

        Parameters
        ----------

        columns:
            List of columns to subset the data.
            If omitted, all columns are returned.
        cast:
            If ``True`` (the default), data will be
            cast according to the ``dtypes`` parameter (if specified)
            or the ``dtypes`` instance attribute.
        dtypes:
            Dictionary mapping column names on
            data types.
        cache:
            Load data from the cache (if avaialble).
            Will be ignored if :func:`enable_cache`
            has been used to enable the cache.


        Returns
        -------
        :
            :class:`pd.DataFrame` containing the data.

        """
        if USE_CACHE or cache:
            if self.source not in CACHE:
                CACHE[self.source] = pd.read_csv(self.source, **self.kwargs)
            df = CACHE[self.source]
            if columns:
                df = df[columns]
        else:
            df = pd.read_csv(self.source, usecols=columns, **self.kwargs)
            if columns:
                df = df[columns]

        if dtypes:
            cast = True
        dtypes = (dtypes or self.dtypes) if cast else {}
        if dtypes:
            for column in df.columns:
                if column in dtypes:
                    try:
                        df[column] = df[column].astype(dtypes[column])
                    except TypeError:
                        df[column] = dtypes[column](df[column])
        return df

    def __call__(self, **kwargs):
        return self.load(**kwargs)


def enable_cache(enable: bool = True):
    """Enable caching for datasets.

    Parameters
    ----------
    enable:
        If ``True`` enable (or reset) the cache.
    """
    global CACHE, USE_CACHE  # pylint: disable=global-statement
    CACHE = {}
    USE_CACHE = enable


def hm2005(
        columns: List[str] = None,
        **kwargs) -> pd.DataFrame:
    r"""
    Data derived from :citet:`hawkins_midgley_2005`.

    The data consists of formant measurements
    taken from 11 RP monopthongs in `hVd`
    contexts produced by twenty male speakers of RP divided
    into four age groups.

    Parameters
    ----------

    columns:
        Specify which columns to return.
        If omitted all columns are returned.

    \*\*kwargs:
        Passed on to :func:`vlnm.data.Dataset.load` method


    Returns
    -------
    :
        A Dataframe containing the data


    Dataset format
    --------------

    group: :class:`pandas.Categorical` of :class:`object`
        Group
    age: :class:`pandas.Categorical` of :class:`object`
        Age label of group
    speaker: :class:`pandas.Categorical` of :class:`np.int64`
        Speaker identifier
    f1 - f2: :class:`np.int64`
        Formant data in Hz
    vowel: :class:`pandas.Categorical` of :class:`object`
        Vowel labels as hVd words.


    Examples
    --------

    .. ipython::

        from vlnm.data import hm2005

        hm2005(['speaker', 'age', 'vowel', 'f1', 'f2']).head()

    """
    return Dataset(
        os.path.join(WHERE_AM_I, 'hm2005.csv'),
        {
            'group': 'category',
            'age': 'category',
            'speaker': 'category',
            'vowel': 'category',
            'f1': np.int64,
            'f2': np.int64,
        }).load(columns=columns, **kwargs)


def pb1952(
        columns: List[str] = None,
        **kwargs) -> pd.DataFrame:
    r"""
    Return data derived from :citet:`peterson_barney_1952`.

    The dataset was extracted from the source files
    for PRAAT :citep:`boersma_weenink_2018` and the
    IPA symbols provided in those files
    replaced with their unicode equivalents.

    Parameters
    ----------

    columns:
        Specify which columns to return.
        If omitted all columns are returned.

    \*\*kwargs:
        Passed on to :func:`vlnm.data.Dataset.load` method


    Returns
    -------
    :
        A Dataframe containing the data


    Dataset format
    --------------

    type: :class:`pandas.Categorical` of :class:`object`
        Type of speaker (child, man or woman)
    sex: :class:`pandas.Categorical` of :class:`object`
        Reported gender of speaker
    speaker: :class:`pandas.Categorical` of :class:`np.int64`
        Speaker identifier
    vowel: :class:`pandas.Categorical` of :class:`object`
        Vowel labels
    IPA: :class:`pandas.Categorical` of :class:`object`
        IPA symbol
    f0 :class:`np.int64`
        Fundamental frequency in Hz.
    f1 - f3: :class:`np.int64`
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
            'type': 'category',
            'sex': 'category',
            'speaker': 'category',
            'vowel': 'category',
            'IPA': 'category',
            'f0': np.int64,
            'f1': np.int64,
            'f2': np.int64,
            'f3': np.int64
        }).load(columns=columns, **kwargs)
