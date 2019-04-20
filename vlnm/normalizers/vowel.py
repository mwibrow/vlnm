"""
Vowel intrinsic normalizers
~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from typing import Callable, List, Union

import pandas as pd
import numpy

from .base import classify, register
from .base import FxNormalizer
from ..conversion import hz_to_bark
from ..docstrings import docstring


@docstring
@register('barkdiff')
@classify(vowel='intrinsic', formant='extrinsic', speaker='intrinsic')
class BarkDifferenceNormalizer(FxNormalizer):
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

    {% f0 %}
    {% f1 %}
    {% f2 %}
    {% f3 %}
    {% rename %}
    transform:
        Replace the function that transforms formants from
        the Hz scale to the Bark scale.
        The function should take numpy array-compatible data structure
        (e.g., :py:class:`pandas.DataFrame`, or :py:class:`numpy.ndarray`)
        *containing only the formant data*,
        and return the transformed data.

    Example
    -------

    The :class:`BarkDifference` normalizer returns columns
    :col:`z1` (if :math:`F_0` is present), :col:`z2`, :col:`z3`:

    .. ipython::

        import pandas as pd
        from vlnm import BarkDifferenceNormalizer

        normalizer = BarkDifferenceNormalizer()
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
            formants: List[str] = None,
            rename: str = None,
            transform: Callable[[pd.DataFrame], pd.DataFrame] = None,
            **kwargs):
        super().__init__(
            f0=f0, f1=f1, f2=f2, f3=f3,
            rename=rename, transform=transform, **kwargs)

    @docstring
    def normalize(
            self,
            df: pd.DataFrame,
            f0: Union[str, List[str]] = None,
            f1: Union[str, List[str]] = None,
            f2: Union[str, List[str]] = None,
            f3: Union[str, List[str]] = None,
            rename: str = None,
            transform: Callable[[numpy.ndarray], numpy.ndarray] = None,
            **kwargs) -> pd.DataFrame:
        r"""Normalize formant data.

        Parameters
        ----------
        df :
            DataFrame containing formant data.

        Other parameters
        ----------------
        :
            For the other parameters see the constructor.

        Returns
        -------
        :

            A dataframe containing the normalized formants.
        """
        return super().normalize(
            df, f0=f0, f1=f1, f2=f2, f3=f3,
            rename=rename, transform=transform)

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
