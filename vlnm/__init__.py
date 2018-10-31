"""
VLNM module
~~~~~~~~~~~
"""
import os

import pandas as pd

from vlnm.normalizers import get_normalizer, list_normalizers

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
    """Read csv file."""

    if DATA_DIR:
        try:
            return pd.read_csv(os.path.join(DATA_DIR, data), *args, **kwargs)
        except (IOError, FileNotFoundError):
            pass
    return pd.read_csv(data, *args, **kwargs)

def normalize(data, *args, method=None, **kwargs):
    """Normalize vowel data in a pandas dataframe.

    """
    try:
        df = read_csv(data)
    except TypeError:
        df = data

    try:
        return method.normalize(df, *args, **kwargs)
    except AttributeError:
        try:
            return method().normalize(df, *args, **kwargs)
        except TypeError:
            return get_normalizer(method)().normalize(
                df, *args, **kwargs)


def normlize_csv(file_in, file_out=None, method=None, **kwargs):
    """Normalize a csv file and save the result.
    """
    df = read_csv(file_in)
    df_norm = normalize(df, method, **kwargs)
    if file_out:
        df_norm.to_csv(file_out, header=True, index=False)
    return df_norm
