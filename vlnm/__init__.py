"""
VLNM module
~~~~~~~~~~~
"""
import os

import pandas as pd

from vlnm.registration import (
    get_normalizer,
    list_normalizers,
    register_normalizer)

from vlnm.normalizers.centroid import (
    WattFabricius1Normalizer,
    WattFabricius2Normalizer,
    WattFabricius3Normalizer,
    WattFabriciusNormalizer)
from vlnm.normalizers.gender import (
    BladenNormalizer,
    NordstromNormalizer)
from vlnm.normalizers.speaker import (
    LCENormalizer,
    LobanovNormalizer,
    NearyGMNormalizer,
    NearyNormalizer)
from vlnm.normalizers.formant import (
    BarkNormalizer,
    ErbNormalizer,
    Log10Normalizer,
    LogNormalizer,
    MelNormalizer)
from vlnm.normalizers.vowel import (
    BarkDifferenceNormalizer)

DATA_DIR = ''


def read_csv(data, *args, **kwargs):
    """Read a csv file.

    Parameters
    ----------

    data : :obj:`str` or :obj:`File`
        A path to a file containing the data,
        a file handle to an open file containing the data.

    *args :
        Passed on to `pandas.read_csv`.

    Keywords
    --------

    **kwargs :
        Passed on to `pandas.read_csv`.

    Returns
    -------

    An instance of `pandas.DataFrame`.

    """
    data_dir = kwargs.pop('data_dir', DATA_DIR)
    if data_dir:
        return pd.read_csv(os.path.join(data_dir, data), *args, **kwargs)
    return pd.read_csv(data, *args, **kwargs)


def normalize(data, file_out=None, method='default', sep=',', **kwargs):
    """Normalize vowel data in a pandas dataframe.

    Parameters
    ----------

    data : :obj:`str` or :obj:`File` or :obj:`DataFrame`
        A path to a file containing the data,
        a file handle to an open file containing the data,
        or a data-frame containing the data

    Keywords
    --------
    file_out : obj:`str` or obj:`File`
        If specified, a file path or a file handle
        to which the output data will be saved (using `DataFrame.to_csv`).
    method : :obj:`str`
        The name of a normalization method.
        Method names can be found using the `list_normalizer` function.
    sep : :obj:`str`
        The column separator in a file.
    **kwargs :
        Other keyword arguments passed on to the normalizer class.


    Returns:
        A `DataFrame` containing the normalized data.
    """
    try:
        df = read_csv(data, sep=sep, header=0)
    except (TypeError, ValueError):
        df = data

    try:
        df_norm = method.normalize(df, **kwargs)
    except (AttributeError, TypeError):
        try:
            df_norm = method().normalize(df, **kwargs)
        except TypeError:
            df_norm = get_normalizer(method)().normalize(
                df, **kwargs)

    if file_out:
        df_norm.to_csv(file_out, sep=sep, header=True, index=False)
    return df_norm
