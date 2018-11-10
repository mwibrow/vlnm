"""
Formant intrinsic normalizers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import numpy as np

from vlnm.normalizers.base import FormatIntrinsicTransformableNormalizer

from vlnm.conversion import (
    hz_to_bark,
    hz_to_erb,
    hz_to_mel)


class BarkNormalizer(FormatIntrinsicTransformableNormalizer):
    r"""
    Normalise vowels using the Bark scale.

    .. math::

        F_i^N =  26.81 \ln\left(
            1 + \frac{F_i}{F_i + 1960}
            \right) - 0.53

    """
    config = dict(transform=hz_to_bark)


class ErbNormalizer(FormatIntrinsicTransformableNormalizer):
    r"""
    Normalise vowels

    .. math::

       F_i^N = 21.4 \ln\left(1 + 0.00437{F_i}\right)

    {{columns}}
    """
    config = dict(transform=hz_to_erb)

class Log10Normalizer(FormatIntrinsicTransformableNormalizer):
    r"""
    Normalize using the base 10 logarithm of the formant values.

     .. math::

       F_i^N = \log_{10}\left(F_i\right)

    """
    config = dict(transform=np.log10)


class LogNormalizer(FormatIntrinsicTransformableNormalizer):
    r"""
    Normalize using the natural logarithm of the formant values.

     .. math::

       F_i^N = \log\left(F_i\right)

    """
    config = dict(transform=np.log)


class MelNormalizer(FormatIntrinsicTransformableNormalizer):
    r"""
    Normalise vowels using the Mel scale.

    .. math::

       F_i^N = 1127 \ln\left(1 + \frac{F_i}{700}\right)

    {{columns}}
    """
    config = dict(transform=hz_to_mel)
