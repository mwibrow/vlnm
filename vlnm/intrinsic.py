"""
Intrinsic vowel normalization
"""

import numpy as np
import pandas as pd


def hz_to_bark(x):
    r"""
    Convert Hz to bark scale.

    .. math::

       x^\prime = 26.81 \displayfrac{x}{x + 1960}\right)

    """
    return 26.81 * x / (x + 1960) - 0.53

def hz_to_mel(x):
    r"""
    Convert Hz to mel scale.

    .. math::

       x^\prime = 1127\log\left(1 + \displayfrac{x}{700}\right)

    """
    return 1127. * np.log(1. + x / 700.)

def log10norm(df, formants, **kwargs):
    r"""
    Base 10 logarithm of formants.

    .. math::

       F_i^N = \log_{10}\left(F_i\right)

    """
    def log10_helper(df, cols, *_, **__):
        return np.log10(df[cols])

    return intrinsics_helper(
        log10_helper,
        df,
        formants,
        **kwargs)

def lognorm(df, formants, **kwargs):
    r"""
    Natural logarithm of formants.

    .. math::

       F_i^N = \ln\left(F_i\right)

    """
    def log_helper(df, cols, *_, **__):
        return np.log(df[cols])
    return intrinsics_helper(
        log_helper,
        df,
        formants,
        **kwargs)

def mel(df, formants, **kwargs):
    r"""
    Normalise vowels

    .. math::

       F_i^N = 1127 \ln\left(1 + \displayfrac{F_i}{700}\right)

    """
    def mel_helper(df, cols, *_, **__):
        return hz_to_mel(df[cols])

    return intrinsics_helper(
        mel_helper,
        df,
        formants,
        **kwargs)

def erb(df, formants, **kwargs):
    r"""
    Normalise vowels

    .. math::

       F_i^N = 21.4 \ln\left(1 + 0.00437{F_i}\right)

    """
    def erb_helper(df, cols, *_, **__):
        return 21.4 * np.log(1 + 0.00437 * df[cols])
    return intrinsics_helper(
        erb_helper,
        df,
        formants,
        **kwargs)

def bark(df, formants, **kwargs):
    r"""
    Normalise vowels using the

    .. math::

        F_i^N =  26.81 \ln\left(
            1 + \displayfrac{F_i}{\displayfrac{F_i} + 1960}
            \right) - 0.53
    """

    def bark_helper(df, cols, *_, **__):
        return 26.81 * df[cols] / (df[cols] + 1960) - 0.53

    return intrinsics_helper(
        bark_helper,
        df,
        formants,
        **kwargs)

def bladen(df, formants, gender='gender', female='F', **kwargs):
    r"""
    .. math::

        F_{ik}^N = 26.81 \ln\left(
            1 + \displayfrac{F_i}{\displayfrac{F_i} + 1960}
            \right) - 0.53 - I(s_k)

    Where :math:`I(s_k)` is an indicator function returning 1 if speaker :math:`k` is
    female and 0 otherwise.

    Parameters
    ----------
    df: pandas.DataFrame
    formants: str / list[str]
    """

    def bladen_helper(df, cols, gender=None, female=None, *_, **__):
        indicator = np.repeat(
            np.atleast_2d(
                (df[gender] == female).astype(float)),
            len(cols),
            axis=0).T
        return 26.81 * df[cols] / (df[cols] + 1960) - 0.53 - indicator

    return intrinsics_helper(
        bladen_helper,
        df,
        formants,
        gender=gender,
        female=female,
        **kwargs)



def bark_difference(df, formants, z0=False, **kwargs):
    """
    Normalize F1 and F2 using the Bark difference method.

    .. math::

        F_{i}^N = Z_3 - Z_i

    Where, :math:`Z_i = 26.81 * F_i / (F_i + 1960) - 0.53`

    """

    def bark_helper(df, cols, z0=False, **kwargs):
        f0, f1, f2, f3 = cols

        df_kwargs = {}
        if f2:
            df_kwargs[f2] = hz_to_bark(df[f3]) - hz_to_bark(df[f2])
        if f1:
            if z0:
                df_kwargs[f1] = hz_to_bark(df[f1]) - hz_to_bark(df[f0])
            else:
                df_kwargs[f1] = hz_to_bark(df[f3]) - hz_to_bark(df[f1])
        return pd.DataFrame(df_kwargs)

    return intrinsics_helper(
        bark_helper,
        df,
        formants,
        z0=z0,
        **kwargs)


def intrinsics_helper(helper, df, formants, margins=None, **kwargs):
    """
    Internal function to assist intrinsic vowel normaliaztion.
    """
    columns = []
    if isinstance(formants, list):
        columns = formants
    else:
        for value in formants.values():
            if value:
                columns.extend(value)
    suffix = kwargs.get('suffix', '')
    if suffix:
        out_columns = ['{}{}'.format(column, suffix) for column in columns]
    else:
        out_columns = columns

    if margins:
        norm_df = pd.DataFrame()
        for _, group_df in df.groupby(by=margins, as_index=False):
            group_norm_df = group_df.copy()
            group_norm_df[out_columns] = helper(group_df, columns, **kwargs)
            norm_df = pd.concat([
                norm_df,
                group_norm_df
            ])
    else:
        norm_df = df.copy()
        norm_df[out_columns] = helper(norm_df, columns, **kwargs)
    return norm_df.reset_index()
