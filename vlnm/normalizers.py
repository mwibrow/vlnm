"""
Normalization methods.
"""

import numpy as np

from vlnm.conversion import (
    hz_to_bark,
    hz_to_mel,
    hz_to_erb)

from vlnm.normalize import VowelNormalizer


class FormantIntrinsicNormalizer(VowelNormalizer):
    r"""
    Base class for formant-intrinsic normaliztion.
    """

    one_of = ['formants', 'f0', 'f1', 'f2', 'f3']

    def _normalize_df(self, df, cols_in, cols_out, **__):
        cols_in = [col for col in cols_in if col]
        cols_out = [col for col in cols_out if col]
        df[cols_in] = df[cols_out]
        return df

    def normalize(self, df, **_):
        """
        Normalize the a data frame.

        Paramters
        ---------
        df: pandas.DataFrame
        """
        return self._normalize(
            df,
            [],
            [self._normalize_df])

class Log10Normalizer(FormantIntrinsicNormalizer):
    r"""
    Normalize using the base 10 logarithm of the formant values.

     .. math::

       F_i^N = \log_{10}\left(F_i\right)
    """

    def _normalize_df(self, df, cols_in, cols_out, **__):
        """
        Normalize using log10
        """
        cols_in = [col for col in cols_in if col]
        cols_out = [col for col in cols_out if col]
        df[cols_out] = np.log10(df[cols_in])
        return df


class LogNormalizer(FormantIntrinsicNormalizer):
    r"""
    Normalize using the natural logarithm of the formant values.

     .. math::

       F_i^N = \log\left(F_i\right)
    """

    one_of = ['formants', 'f0', 'f1', 'f2', 'f3']

    def _normalize_df(self, df, cols_in, cols_out, **__):
        """
        Normalize using log10
        """
        cols_in = [col for col in cols_in if col]
        cols_out = [col for col in cols_out if col]
        df[cols_out] = np.log(df[cols_in])
        return df


class MelNormalizer(FormantIntrinsicNormalizer):
    r"""
    Normalise vowels using the Mel scale.

    .. math::

       F_i^N = 1127 \ln\left(1 + \displayfrac{F_i}{700}\right)

    """
    def _normalize_df(self, df, cols_in, cols_out, **__):
        cols_in = [col for col in cols_in if col]
        cols_out = [col for col in cols_out if col]
        df[cols_out] = hz_to_mel(df[cols_in])
        return df


class BarkNormalizer(FormantIntrinsicNormalizer):
    r"""
    Normalise vowels using the Bark scale.

    .. math::

        F_i^N =  26.81 \ln\left(
            1 + \displayfrac{F_i}{\displayfrac{F_i} + 1960}
            \right) - 0.53
    """
    def _normalize_df(self, df, cols_in, cols_out, **__):
        df[cols_out] = hz_to_bark(df[cols_in])
        return df


class ErbNormalizer(FormantIntrinsicNormalizer):
    r"""
    Normalise vowels

    .. math::

       F_i^N = 21.4 \ln\left(1 + 0.00437{F_i}\right)

    """
    def _normalize_df(self, df, cols_in, cols_out, **__):
        cols_in = [col for col in cols_in if col]
        cols_out = [col for col in cols_out if col]
        df[cols_out] = hz_to_erb(df[cols_in])
        return df
