"""
Vowel intrinsic normalizers
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. normalizers-list::
    :module: vlnm.normalizers.vowel

"""
from typing import Callable, List, Union

import pandas as pd
import numpy as np

from .base import classify, register
from .base import FormantSpecificNormalizer
from ..conversion import hz_to_bark
from ..docstrings import docstring


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


@classify(formant='extrinsic', vowel='intrinsic', speaker='extrinsic')
class AnanthapadmanabhaRamakrishnanNormalizer(FormantSpecificNormalizer):
    r"""
    Normalize formant data according to :citet:`ananthapadmanabha_ramakrishnan_2016`.

    Let the data consist of a set of :math:`I` formants
    (where :math:`i\in I\implies 1\leq i\leq3`)
    for  :math:`J` vowels from :math:`K` speakers.

    Let :math:`G_{k}` be the geometric mean of the
    first, second and third formants for a speaker :math:`k\in K`:

    .. math::

        G_{k} = \left(\prod_{i=1}^{3} F_{ik}\right)^{\frac{1}{3}}

    Then let :math:`F_{ik}^*` be the normalized value of the
    formant :math:`F_i` for speaker :math:`k`:

    .. math::

        F_{ik}^* = \frac{F_{ik}}{G_{ik}}


    This normalized value is then 'denormalized'
    with respect to vowel :math:`j\in J` so that
    that :math:`F_{ijk}^\prime` repesents the denormalized
    value of formant :math:`i` for spekaer :math:`k`
    with respect to vowel :math:`j`:

    .. math::

        F_{ijk}^\prime = F_{ik}^* \mu_{ij}

    where :math:`\mu_{ij}` is the mean value of formant
    :math:`i` for vowel :math:`j`.
    Normalization is completed by calcluating
    the distance between the denormalized formant
    values to those of prototypical vowels,
    and by classifying each vowel
    according to the closest prototype.
    Vowel prototypes are bootstrapped from the sample.




    .. math::

        \mbox{argmin}_{j \in J} = \Delta\left(F_{ijk}^\prime)

    Where :math:`\Delta` is a distance metric which
    :citet:`ananthapadmanabha_ramakrishnan_2016`
    define as:

    .. math::

        \Delta_{ijk}() = \sum_{i=1}^{2}\frac{F_{ijk}^\prime - \mu_{ij}}{\sigma_{ij}}

    """
