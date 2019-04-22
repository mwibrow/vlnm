"""
VLNM module
~~~~~~~~~~~
"""

import io
import os
from typing import Dict, List, Optional, Union
import sys

import pandas as pd

from vlnm.registration import (
    NORMALIZERS,
    get_normalizer,
    register_normalizer)

from vlnm.normalizers.base import (
    DefaultNormalizer,
    Normalizer)

from vlnm.normalizers.centroid import (
    WattFabricius1Normalizer,
    WattFabricius2Normalizer,
    WattFabricius3Normalizer,
    WattFabriciusNormalizer)
from vlnm.normalizers.gender import (
    BladenNormalizer,
    NordstromNormalizer)
from vlnm.normalizers.speaker import (
    GerstmanNormalizer,
    LCENormalizer,
    LobanovNormalizer,
    NearyExpNormalizer,
    NearyGMNormalizer,
    NearyGMExpNormalizer,
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
        sep: str = ',', **kwargs) -> Optional[pd.DataFrame]:
    """Normalize vowel data.

    Parameters
    ----------

    data:
        A path to a CSV file containing the data,
        a file handle to an open file containing the data,
        or a Pandas :class:`DataFrame` containing the data.
    file_out:
        An optional a file path or a file handle
        to which the output data will be saved (using ``DataFrame.to_csv``).
    method:
        The name of a normalization method.
        Method names can be found using the :func:`list_normalizers` function.
    sep:
        The column separator in a file.
    **kwargs :
        Other keyword arguments passed on to the normalizer class.


    Returns
    -------
    :
        If ``file_out`` is not specified, a Pandas :class:`DataFrame`
        containing the normalized data.
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


def list_normalizers(sort: bool = True, module: str = None, index: Dict = None) -> List[str]:
    """Return a list of available normalizers.

    Parameters
    ----------
    sort:
        Whether to sort the list by alphabetical order
    module:
        List normalizers in the specified module.
        If omitted, all available normalizers will be listed.
    index:
        The register in which the normalizer was registered.
        If omitted, the global register will be used.

    Returns
    -------
    :
        A list containing the names of the available normalizers.

    Example
    -------

    .. ipython::

        from vlnm import list_normalizers
        list_normalizers()

    """
    index = index if index is not None else NORMALIZERS
    names = list(index.keys())
    if sort:
        names = sorted(names)
    if module:
        filtered = []
        for name in names:
            normalizer = get_normalizer(name)
            if normalizer.__module__.startswith(module):
                filtered.append(name)
        names = filtered
    return names
