"""
Formant intrinsic normalizers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import numpy as np

from vlnm.normalizers.base import (
    FormantIntrinsicNormalizer)
from vlnm.conversion import (
    hz_to_bark,
    hz_to_erb,
    hz_to_mel)
from vlnm.decorators import (
    Columns,
    DocString,
    Keywords,
    Register)

@Register('bark')
@DocString
@Columns(
    choice=dict(
        formants=['f0', 'f1', 'f2', 'f3']
    )
)
@Keywords(
    optional=['hz_to_bark']
)
class BarkNormalizer(FormantIntrinsicNormalizer):
    r"""
    Normalise vowels using the Bark scale.

    .. math::

        F_i^N =  26.81 \ln\left(
            1 + \frac{F_i}{F_i + 1960}
            \right) - 0.53

    {{columns}}
    {{keywords}}
    """
    @staticmethod
    def _norm(df, **kwargs):
        """
        Transform formants.
        """
        formants = kwargs.get('formants')
        convert = kwargs.get('hz_to_bark', hz_to_bark)
        df[formants] = convert(df[formants])
        return df

@Register('erb')
@DocString
@Columns(
    choice=dict(
        formants=['f0', 'f1', 'f2', 'f3']
    )
)
@Keywords(
    optional=['hz_to_erb']
)
class ErbNormalizer(FormantIntrinsicNormalizer):
    r"""
    Normalise vowels

    .. math::

       F_i^N = 21.4 \ln\left(1 + 0.00437{F_i}\right)

    {{columns}}
    """
    @staticmethod
    def _norm(df, **kwargs):
        """
        Transform formants.
        """
        formants = kwargs.get('formants')
        convert = kwargs.get('hz_to_erb', hz_to_erb)
        df[formants] = convert(df[formants])
        return df


@Register('log10')
@DocString
@Columns(
    choice=dict(
        formants=['f0', 'f1', 'f2', 'f3']
    )
)
@Keywords(
    optional=['aliases', 'rename']
)
class Log10Normalizer(FormantIntrinsicNormalizer):
    r"""
    Normalize using the base 10 logarithm of the formant values.

     .. math::

       F_i^N = \log_{10}\left(F_i\right)

    """
    @staticmethod
    def _norm(df, **kwargs):
        """
        Transform formants.
        """
        formants = kwargs.get('formants')
        df[formants] = np.log10(df[formants])
        return df


@Register('log')
@DocString
@Columns(
    choice=dict(
        formants=['f0', 'f1', 'f2', 'f3']
    )
)
class LogNormalizer(FormantIntrinsicNormalizer):
    r"""
    Normalize using the natural logarithm of the formant values.

     .. math::

       F_i^N = \log\left(F_i\right)

    {{columns}}
    """
    @staticmethod
    def _norm(df, **kwargs):
        """
        Transform formants.
        """
        formants = kwargs.get('formants')
        df[formants] = np.log(df[formants])
        return df


@Register('mel')
@DocString
@Columns(
    choice=dict(
        formants=['f0', 'f1', 'f2', 'f3']
    )
)
@Keywords(
    optional=['hz_to_mel']
)
class MelNormalizer(FormantIntrinsicNormalizer):
    r"""
    Normalise vowels using the Mel scale.

    .. math::

       F_i^N = 1127 \ln\left(1 + \frac{F_i}{700}\right)

    {{columns}}
    """
    @staticmethod
    def _norm(df, **kwargs):
        """
        Transform formants.
        """
        formants = kwargs.get('formants')
        convert = kwargs.get('hz_to_mel', hz_to_mel)
        df[formants] = convert(df[formants])
        return df
