"""
VLNM module
~~~~~~~~~~~
"""
import os

import pandas as pd

from vlnm.normalizers import get_normalizer

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
    df = read_csv(data)
    df_norm = normalize(df, method, **kwargs)
    if file_out:
        df.norm.to_csv(file_out, header=True, index=False)
    return df_norm