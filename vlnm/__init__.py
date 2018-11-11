"""
VLNM module
~~~~~~~~~~~
"""
import os

import pandas as pd

from vlnm.normalizers import (
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
    """Read csv file."""

    if DATA_DIR:
        try:
            return pd.read_csv(os.path.join(DATA_DIR, data), *args, **kwargs)
        except (IOError, FileNotFoundError):
            pass
    return pd.read_csv(data, *args, **kwargs)

def normalize(data, *args, method=None, sep=',', header=0, **kwargs):
    """Normalize vowel data in a pandas dataframe.

    """
    try:
        df = read_csv(data, sep=sep, header=header)
    except TypeError:
        df = data

    try:
        df_norm = method.normalize(df, **kwargs)
    except AttributeError:
        try:
            df_norm = method().normalize(df, **kwargs)
        except TypeError:
            df_norm = get_normalizer(method)().normalize(
                df, **kwargs)

    if args:
        output = args[0]
        df_norm.to_csv(output, sep=sep, header=True, index=False)
    return df_norm

def normlize_csv(file_in, file_out=None, method=None, **kwargs):
    """Normalize a csv file and save the result.
    """
    df = read_csv(file_in)
    df_norm = normalize(df, method, **kwargs)
    if file_out:
        df_norm.to_csv(file_out, header=True, index=False)
    return df_norm
