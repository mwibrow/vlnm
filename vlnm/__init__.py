"""
VLNM module
~~~~~~~~~~~
"""

import io
import os
from typing import Union
import sys

import pandas as pd

from vlnm.registration import (
    get_normalizer,
    list_normalizers,
    register_normalizer)

from vlnm.normalizers.base import Normalizer

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


def normalize(
        data: Union[str, io.TextIOWrapper, pd.DataFrame],
        file_out: Union[str, io.TextIOWrapper] = None,
        method: str = 'default',
        sep: str = ',', **kwargs):
    """Normalize vowel data in a pandas dataframe.

    Parameters
    ----------

    data:
        A path to a file containing the data,
        a file handle to an open file containing the data,
        or a data-frame containing the data.
    file_out:
        If specified, a file path or a file handle
        to which the output data will be saved (using `DataFrame.to_csv`).
    method:
        The name of a normalization method.
        Method names can be found using the `list_normalizer` function.
    sep:
        The column separator in a file.
    **kwargs :
        Other keyword arguments passed on to the normalizer class.


    Returns:
        A `DataFrame` containing the normalized data.
    """
    try:
        df = pd.read_csv(data, sep=sep, header=0)
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
        return None
    return df_norm
