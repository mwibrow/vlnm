"""
Normalizers
"""
import numpy as np

from vlnm.conversion import (
    hz_to_bark,
    hz_to_erb,
    hz_to_mel)
from vlnm.decorators import (
    docstring as DocString,
    columns as Columns)
from vlnm.normalize import (
    VowelNormalizer,
    FormantIntrinsicNormalizer)

@DocString
@Columns(
    formants=['f0', 'f1', 'f2', 'f3']
)
class Log10Normalizer(FormantIntrinsicNormalizer):
    r"""
    Normalize using the base 10 logarithm of the formant values.

     .. math::

       F_i^N = \log_{10}\left(F_i\right)

    {{columns}}
    """
    def transform(self, df):
        """
        Transform formants.
        """
        return np.log10(df)


@DocString
@Columns(
    formants=['f0', 'f1', 'f2', 'f3']
)
class LogNormalizer(FormantIntrinsicNormalizer):
    r"""
    Normalize using the natural logarithm of the formant values.

     .. math::

       F_i^N = \log\left(F_i\right)

    {{columns}}
    """
    def transform(self, df, **_):
        """
        Transform formants.
        """
        return np.log(df)



@DocString
@Columns(
    formants=['f0', 'f1', 'f2', 'f3']
)
class MelNormalizer(FormantIntrinsicNormalizer):
    r"""
    Normalise vowels using the Mel scale.

    .. math::

       F_i^N = 1127 \ln\left(1 + \displayfrac{F_i}{700}\right)

    {{columns}}
    """
    def transform(self, df, **_):
        """
        Transform formants.
        """
        return hz_to_mel(df)

@DocString
@Columns(
    formants=['f0', 'f1', 'f2', 'f3']
)
class BarkNormalizer(FormantIntrinsicNormalizer):
    r"""
    Normalise vowels using the Bark scale.

    .. math::

        F_i^N =  26.81 \ln\left(
            1 + \displayfrac{F_i}{\displayfrac{F_i} + 1960}
            \right) - 0.53

    {{columns}}
    """
    def transform(self, df, **_):
        """
        Transform formants.
        """
        return hz_to_bark(df)

@DocString
@Columns(
    formants=['f0', 'f1', 'f2', 'f3']
)
class ErbNormalizer(FormantIntrinsicNormalizer):
    r"""
    Normalise vowels

    .. math::

       F_i^N = 21.4 \ln\left(1 + 0.00437{F_i}\right)

    {{columns}}
    """
    def transform(self, df, **_):
        """
        Transform formants.
        """
        return hz_to_erb(df)
