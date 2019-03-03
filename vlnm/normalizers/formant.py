"""
Formant intrinsic normalizers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import numpy as np

from ..docstrings import docstring
from .base import register_class, FormatIntrinsicTransformableNormalizer



from ..conversion import (
    hz_to_bark,
    hz_to_erb,
    hz_to_mel)

@docstring
@register_class('bark')
class BarkNormalizer(FormatIntrinsicTransformableNormalizer):
    r"""Normalise formants using the Bark scale :citet:`traunmuller_1990`.

    .. math::

        F_i^N =  26.81 \ln\left(
            1 + \frac{F_i}{F_i + 1960}
            \right) - 0.53

    Parameters
    ----------
    {% formants %}
    {% rename %}
    transform:
        Replace the function that transforms formants from
        the Hz scale to the Bark scale.
        The function should take numpy array-compatible data structure
        (e.g., :py:class:`numpy.ndarray`, :py:class:`pandas.DataFrame`, etc.)
        and return the transformed data.

    """
    config = dict(transform=hz_to_bark)


@docstring
@register_class('erb')
class ErbNormalizer(FormatIntrinsicTransformableNormalizer):
    r"""
    Normalise formants using the ERB scale :citep:`moore_glasberg_1996`.

    .. math::

       F_i^N = 21.4 \ln\left(1 + 0.00437{F_i}\right)

    Parameters
    ----------
    {% formants %}
    {% rename %}
    transform:
        Replace the function that transforms formants from
        the Hz scale to the ERB scale.
        The function should take numpy array-compatible data structure
        (e.g., :py:class:`numpy.ndarray`, :py:class:`pandas.DataFrame`, etc.)
        and return the transformed data.
    """
    config = dict(transform=hz_to_erb)


@docstring
@register_class('log10')
class Log10Normalizer(FormatIntrinsicTransformableNormalizer):
    r"""
    Normalize using the base 10 logarithm of the formant values.

     .. math::

       F_i^N = \log_{10}\left(F_i\right)

    Parameters
    ----------
    {% formants %}
    {% rename %}
    """
    config = dict(transform=np.log10)


@docstring
@register_class('log')
class LogNormalizer(FormatIntrinsicTransformableNormalizer):
    r"""
    Normalize using the natural logarithm of the formant values.

     .. math::

       F_i^N = \log\left(F_i\right)

    Parameters
    ----------
    {% formants %}
    {% rename %}
    """
    config = dict(transform=np.log)

@docstring
@register_class('mel')
class MelNormalizer(FormatIntrinsicTransformableNormalizer):
    r"""
    Normalise vowels using the Mel scale :citep:`see {% oshaughnessy_1987 %}, p.150`.

    .. math::

       F_i^N = 1127 \ln\left(1 + \frac{F_i}{700}\right)

    Parameters
    ----------
    {% formants %}
    {% rename %}
    transform:
        Replace the function that transforms formants from
        the Hz scale to the Mel scale.
        The function should take numpy array-compatible data structure
        (e.g., :py:class:`numpy.ndarray`, :py:class:`pandas.DataFrame`, etc.)
        and return the transformed data.
    """
    config = dict(transform=hz_to_mel)
