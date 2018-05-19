"""
Module for vowel normalization
"""

import numpy as np
import pandas as pd

from vlmn.methods import lobanov

METHODS = {
    'lobanov': lobanov
}


def normalize(
        data,
        vowel,
        formants,
        margins=None,
        method='lobanov',
        **kwargs):
    """
    Normalize vowel formants.
    """
    if method not in METHODS:
        raise ValueError('Invalid normalisation method {}'.format(method))
    call = METHODS[method]
    formants = dict(
        f0=formants.get('f0', formants.get('F0')),
        f1=formants.get('f1', formants.get('F1')),
        f2=formants.get('f2', formants.get('F2')),
        f3=formants.get('f3', formants.get('F3')))
    if margins:
        norm_df = data.groupby(margins, as_index=False).apply(
            lambda x: call(x, vowel, formants, **kwargs))
        norm_df = norm_df.reset_index(drop=True)
    else:
        norm_df = data.apply(lambda x: call(x.to_frame().T, vowel, formants, **kwargs), axis=1)
    return norm_df




