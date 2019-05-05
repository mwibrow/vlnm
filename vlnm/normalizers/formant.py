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


@docstring
@register('barkdiff')
@classify(vowel='intrinsic', formant='extrinsic', speaker='intrinsic')
class BarkDifferenceNormalizer(FormantSpecificNormalizer):
    r"""
    Normalize formant data according to :citet:`syrdal_gopal_1986`.

    Vowels are normalized by converting formants to the
    Bark scale, calculating the difference :math:`Z` between
    consecutive formants:

    .. math::

        Z_{i}^\prime = B(F_i) - B(F_{i-1})\mbox{ for } 1 \leq i \leq 3

    Where :math:`B` is a function converting the :math:`i\mbox{th}`
    formant measured in hertz to the Bark scale.



    Parameters
    ----------

    f0 - f3:
    transform:
        Replace the function that transforms formants from
        the Hz scale to the Bark scale.
        The function should take numpy array-compatible data structure
        (e.g., :py:class:`pandas.DataFrame`, or :py:class:`numpy.ndarray`)
        *containing only the formant data*,
        and return the transformed data.


    Other Parameters
    ----------------
    rename:
    groupby:
    kwargs:


    Example
    -------

    The :class:`BarkDifference` normalizer returns columns
    :col:`z1` (if :math:`F_0` is present), :col:`z2`, :col:`z3`:

    .. ipython::
        dataframe:
            formatters:
                float64: '{:.03f}'
        before: |
            SetupCsv(['speaker', 'vowel', 'f0', 'f1', 'f2', 'f3'])

        import pandas as pd
        from vlnm import BarkDifferenceNormalizer

        normalizer = BarkDifferenceNormalizer()
        df = pd.read_csv('vowels.csv')
        norm_df = normalizer.normalize(df)
        norm_df.head()

    To rename these columns, use the ``rename`` argument
    with a dictionary:

    .. ipython::
        dataframe:
            formatters:
                float64: '{:.03f}'
        before: |
            SetupCsv(['speaker', 'vowel', 'f0', 'f1', 'f2', 'f3'])

        normalizer = BarkDifferenceNormalizer(
            rename=dict(z1='f1-f0', z2='f2-f1', z3='f3-f2'))
        df = pd.read_csv('vowels.csv')
        norm_df = normalizer.normalize(df)
        norm_df.head()

    """
    config = dict(
        keywords=['f0', 'f1', 'f2', 'f3'],
        transform=hz_to_bark
    )

    def __init__(
            self,
            f0: Union[str, List[str]] = None,
            f1: Union[str, List[str]] = None,
            f2: Union[str, List[str]] = None,
            f3: Union[str, List[str]] = None,
            transform: Callable[[np.ndarray], np.ndarray] = None,
            rename: Union[str, dict] = None,
            groupby: Union[str, List[str]] = None,
            **kwargs):
        super().__init__(
            f0=f0, f1=f1, f2=f2, f3=f3,
            rename=rename, groupby=groupby, transform=transform, **kwargs)

    @docstring
    def normalize(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        return super().normalize(df, **kwargs)

    def _norm(self, df):

        transform = self.config['transform']
        f0 = self.params['f0']
        f1 = self.params['f1']
        f2 = self.params['f2']
        f3 = self.params['f3']

        z0 = transform(df[f0]) if f0 in df else None
        z1 = transform(df[f1])
        z2 = transform(df[f2])
        z3 = transform(df[f3])

        if z0 is not None:
            df['z1'] = z1 - z0
        df['z2'] = z2 - z1
        df['z3'] = z3 - z2

        return df
