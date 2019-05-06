"""
Formant intrinsic normalizers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


.. normalizers-list::
    :module: vlnm.normalizers.formant


"""
from typing import Callable, List, Union
import numpy as np
import pandas as pd

from ..docstrings import docstring
from .base import (
    classify,
    register,
    FormantSpecificNormalizer,
    FormantsTransformNormalizer)

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

        F_i^* =  26.81 \ln\left(
            1 + \frac{F_i}{F_i + 1960}
            \right) - 0.53

    Parameters
    ----------

    formants:
    transform:
        Replace the function that transforms formants from
        the Hz scale to the Bark scale.
        The function should take numpy array-compatible data structure
        (e.g., :py:class:`numpy.ndarray`, :py:class:`pandas.DataFrame`, etc.)
        and return the transformed data.


    Other parameters
    ----------------
    rename:
    groupby:
    kwargs:


    Example
    -------

    .. ipython::

        import pandas as pd
        from vlnm import BarkNormalizer

        normalizer = BarkNormalizer(rename='{}*')
        df = pd.read_csv('vowels.csv')
        norm_df = normalizer.normalize(df)
        norm_df.head()

    """
    config = dict(transform=hz_to_bark)

    def __init__(
            self,
            formants: List[str] = None,
            transform: Callable[[np.ndarray], np.ndarray] = None,
            rename: Union[str, dict] = None,
            groupby: Union[str, List[str]] = None,
            **kwargs):
        super().__init__(
            formants=formants,
            transform=transform,
            rename=rename,
            groupby=groupby,
            **kwargs)

    @docstring
    def normalize(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        return super().normalize(df)


@docstring
@register('erb')
@classify(vowel='intrinsic', formant='intrinsic', speaker='intrinsic')
class ErbNormalizer(FormantsTransformNormalizer):
    r"""
    Normalise formants using the ERB scale :citep:`moore_glasberg_1996`.

    .. math::

       F_i^* = 21.4 \ln\left(1 + 0.00437{F_i}\right)

    Parameters
    ----------

    formants:
    transform:
        Replace the function that transforms formants from
        the Hz scale to the ERB scale.
        The function should take numpy array-compatible data structure
        (e.g., :py:class:`numpy.ndarray`, :py:class:`pandas.DataFrame`, etc.)
        and return the transformed data.


    Other parameters
    ----------------
    rename:
    groupby:
    kwargs:


    Example
    -------

    .. ipython::

        import pandas as pd
        from vlnm import ErbNormalizer

        normalizer = ErbNormalizer(rename='{}*')
        df = pd.read_csv('vowels.csv')
        norm_df = normalizer.normalize(df)
        norm_df.head()

    """
    config = dict(transform=hz_to_erb)

    def __init__(
            self,
            formants: List[str] = None,
            transform: Callable[[np.ndarray], np.ndarray] = None,
            rename: Union[str, dict] = None,
            groupby: Union[str, List[str]] = None,
            **kwargs):
        super().__init__(
            formants=formants,
            transform=transform,
            rename=rename,
            groupby=groupby,
            **kwargs)

    @docstring
    def normalize(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        return super().normalize(df)


@docstring
@register('log10')
@classify(vowel='intrinsic', formant='intrinsic', speaker='intrinsic')
class Log10Normalizer(FormantsTransformNormalizer):
    r"""
    Normalize using the base 10 logarithm of the formant values.

     .. math::

       F_i^* = \log_{10}\left(F_i\right)


    Parameters
    ----------
    formants:


    Other parameters
    ----------------
    rename:
    groupby:
    kwargs:


    Example
    -------

    .. ipython::

        import pandas as pd
        from vlnm import Log10Normalizer

        normalizer = Log10Normalizer(rename='{}*')
        df = pd.read_csv('vowels.csv')
        norm_df = normalizer.normalize(df)
        norm_df.head()

    """
    config = dict(transform=np.log10)

    def __init__(
            self,
            formants: List[str] = None,
            transform: Callable[[np.ndarray], np.ndarray] = None,
            rename: Union[str, dict] = None,
            groupby: Union[str, List[str]] = None,
            **kwargs):
        super().__init__(
            formants=formants,
            transform=transform,
            rename=rename,
            groupby=groupby,
            **kwargs)

    @docstring
    def normalize(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        return super().normalize(df)


@docstring
@register('log')
@classify(vowel='intrinsic', formant='intrinsic', speaker='intrinsic')
class LogNormalizer(FormantsTransformNormalizer):
    r"""
    Normalize using the natural logarithm of the formant values.

     .. math::

       F_i^* = \log\left(F_i\right)

    Parameters
    ----------

    formants:


    Other parameters
    ----------------
    rename:
    groupby:
    kwargs:


    Example
    -------

    .. ipython::

        import pandas as pd
        from vlnm import LogNormalizer

        normalizer = LogNormalizer(rename='{}*')
        df = pd.read_csv('vowels.csv')
        norm_df = normalizer.normalize(df)
        norm_df.head()

    """
    config = dict(transform=np.log)

    def __init__(
            self,
            formants: List[str] = None,
            transform: Callable[[np.ndarray], np.ndarray] = None,
            rename: Union[str, dict] = None,
            groupby: Union[str, List[str]] = None,
            **kwargs):
        super().__init__(
            formants=formants,
            transform=transform,
            rename=rename,
            groupby=groupby,
            **kwargs)

    @docstring
    def normalize(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        return super().normalize(df)


@docstring
@register('mel')
@classify(vowel='intrinsic', formant='intrinsic', speaker='intrinsic')
class MelNormalizer(FormantsTransformNormalizer):
    r"""
    Normalise vowels using the Mel scale :citep:`see {% oshaughnessy_1987 %}, p.150`.

    .. math::

       F_i^* = 1127 \ln\left(1 + \frac{F_i}{700}\right)

    Parameters
    ----------

    formants:
    transform:
        Replace the function that transforms formants from
        the Hz scale to the Mel scale.
        The function should take numpy array-compatible data structure
        (e.g., :py:class:`numpy.ndarray`, :py:class:`pandas.DataFrame`, etc.)
        and return the transformed data.


    Other parameters
    ----------------
    rename:
    groupby:
    kwargs:


    Example
    -------

    .. ipython::

        import pandas as pd
        from vlnm import MelNormalizer

        normalizer = MelNormalizer(rename='{}*')
        df = pd.read_csv('vowels.csv')
        norm_df = normalizer.normalize(df)
        norm_df.head()

    """
    config = dict(transform=hz_to_mel)

    def __init__(
            self,
            formants: List[str] = None,
            transform: Callable[[np.ndarray], np.ndarray] = None,
            rename: Union[str, dict] = None,
            groupby: Union[str, List[str]] = None,
            **kwargs):
        super().__init__(
            formants=formants,
            transform=transform,
            rename=rename,
            groupby=groupby,
            **kwargs)

    @docstring
    def normalize(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        return super().normalize(df)
