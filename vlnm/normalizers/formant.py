"""
Formant intrinsic normalizers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Formant intrinsic normalizers normalize
formant data
"""
import numpy as np

from ..docstrings import docstring
from .base import classify, register, FormantsTransformNormalizer


from ..conversion import (
    hz_to_bark,
    hz_to_erb,
    hz_to_mel)


@docstring
@register('bark')
@classify(vowel='intrinsic', formant='intrinsic', speaker='intrinsic')
class BarkNormalizer(FormantsTransformNormalizer):
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
@register('erb')
@classify(vowel='intrinsic', formant='intrinsic', speaker='intrinsic')
class ErbNormalizer(FormantsTransformNormalizer):
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
@register('log10')
@classify(vowel='intrinsic', formant='intrinsic', speaker='intrinsic')
class Log10Normalizer(FormantsTransformNormalizer):
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
@register('log')
@classify(vowel='intrinsic', formant='intrinsic', speaker='intrinsic')
class LogNormalizer(FormantsTransformNormalizer):
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
@register('mel')
@classify(vowel='intrinsic', formant='intrinsic', speaker='intrinsic')
class MelNormalizer(FormantsTransformNormalizer):
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
