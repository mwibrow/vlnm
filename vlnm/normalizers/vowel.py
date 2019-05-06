"""

Vowel intrinsic normalizers
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. normalizers-list::
    :module: vlnm.normalizers.vowel


"""

from typing import Callable, List, Union

import numpy as np
import pandas as pd

from ..conversion import hz_to_bark
from ..docstrings import docstring
from .base import register, classify
from .base import uninstantiable, Normalizer, FormantSpecificNormalizer


@docstring
@register('ie-gmagm')
@classify(formant='extrinsic', vowel='intrinsic', speaker='extrinsic')
class IEGMAGMNormalizer(FormantSpecificNormalizer):
    r"""
    Normalize formants according to
    :citet:`{% ananthapadmanabha_ramakrishnan_2016 %}, appendix B`.

    Formants for a given token are
    first normalized by dividing the values in Hz
    by the geometric mean of the first three formants.
    The normalized values are then 'denormalized' by
    multiplying by the geometric mean of
    the means for each vowel across all speakers.
    Equivalently, for a given token of vowel :math:`j`:

    .. math::

        F^*_{ij} = F_{ij}\left(
            \prod_{i=1}^{3}
                \frac{\mu_{ij}}{F_{ij}}
            \right)^{\frac{1}{3}}

    Where :math:`\mu_{ij}` is the mean of :math:`F_i`
    for vowel :math:`j` for all tokens and speakers.

    Parameters
    ----------
    f1 - f3:
    vowel:


    Other Parameters
    ----------------
    rename:
    groupby:
    kwargs:


    Examples
    --------

    .. ipython::
        before: |
            SetupCsv(['speaker', 'vowel', 'f1', 'f2', 'f3'])

        from vlnm import IEGMAGMNormalizer

        normalizer = IEGMAGMNormalizer(rename='{}*')
        norm_df = normalizer.normalize('vowels.csv')
        norm_df.head()

    """

    config = dict(
        columns=['f1', 'f2', 'f3', 'vowel'],
        outputs=['f1', 'f2'],
        keywords=['vowel']
    )

    def __init__(
            self,
            f1: Union[str, List[str]] = None,
            f2: Union[str, List[str]] = None,
            f3: Union[str, List[str]] = None,
            vowel: str = 'vowel',
            rename: Union[str, dict] = None,
            groupby: Union[str, List[str]] = None,
            **kwargs):
        super().__init__(
            f1=f1,
            f2=f2,
            f3=f3,
            vowel=vowel,
            rename=rename,
            **kwargs)

    def _norm(self, df):
        f1, f2, f3 = self.params['f1'], self.params['f2'], self.params['f3']
        vowel = self.params['vowel']
        df[[f1, f2]] = df[[f1, f2]].div(
            np.cbrt(df[[f1, f2, f3]].apply(np.prod, axis=1)), axis=0).mul(
                np.cbrt(np.prod(df[[f1, f2, f3]].mean(axis=0))), axis=1)
        return df


@docstring
@register('ie-ht')
@classify(formant='extrinsic', vowel='intrinsic', speaker='extrinsic')
class IEHTNormalizer(FormantSpecificNormalizer):
    r"""
    Normalize (and potentially relabel) formants
    according in :citet:`{% ananthapadmanabha_ramakrishnan_2016 %}`.

    Let :math:`F^{\prime}_{ij}` be the raw formant value in Hz
    for a particular token of vowel :math:`j`
    divided by the gemometric mean of the first three formants for
    that token:

    .. math::

        F^{\prime}_{ij} = \frac{F_{ij}}
            { \left( \prod_{i=1}^{3}F_{ij} \right)^{\frac{1}{3}} }

    Let :math:`\mu_{ij}` be the mean of :math:`F_i`
    for vowel :math:`j` for all tokens and speakers,
    and define :math:`F^{\prime\prime}_{ij}` as follows:

    .. math::

        F^{\prime\prime}_{ij} = F^{\prime}_{ij}\mu_{ij}

    Then let :math:`\mu^{\prime\prime}_{ij}` and :math:`\sigma^{\prime\prime}_{ij}`
    be the mean and standard deviation, respectively,
    of :math:`F^{\prime\prime}_i` for vowel :math:`j` for all tokens and
    speakers.
    Then the normalized value can be calulated as follows:

    .. math::

        F^*_{ij^*} = F^\prime_{ij} \mu_{ij^*}


    Where :math:`j^*` is vowel from the set of vowels :math:`J`
    such that:

    .. math::

        j^* = \underset{j \in J}{\text{argmin}}
            \left(
                \sum_{i=1}^{2}\left(
                    \frac{F^\prime_{ij}\mu_{ij} - \mu^{\prime\prime}_{ij}}
                        {\sigma^{\prime\prime}_{ij}}
                \right)^2
            \right)^{\frac{1}{2}}


    .. note::

        :citet:`ananthapadmanabha_ramakrishnan_2016` appear
        to suggest the use of :math:`F^\prime_{ij}\mu^{\prime\prime}_{ij}`
        when calculating :math:`j^*`. However, this produces
        meaningless results (and certainly not the results that
        they report) so :math:`F^\prime_{ij}\mu_{ij}` is used
        in this implementation.


    Parameters
    ----------
    f1 - f3:
    vowel:


    Other Parameters
    ----------------
    rename:
    groupby:
    kwargs:


    Examples
    --------

    As the :class:`IEHTNormalizer` can relabel vowels
    it also updates the :col:`vowel` column.
    The ``rename`` argument can be used to keep the
    old labels.

    .. ipython::
        dataframe:
            formatters:
                float64: '{:.03f}'
        before: |
            SetupCsv(['speaker', 'vowel', 'f1', 'f2', 'f3'])

        import pandas as pd
        from vlnm import IEHTNormalizer

        normalizer = IEHTNormalizer(rename='{}*')
        df = pd.read_csv('vowels.csv')
        norm_df = normalizer.normalize(df)
        norm_df.head()

    """

    config = dict(
        columns=['f1', 'f2', 'f3', 'vowel'],
        outputs=['f1', 'f2', 'vowel'],
        keywords=['vowel']
    )

    def __init__(
            self,
            f1: Union[str, List[str]] = 'f1',
            f2: Union[str, List[str]] = 'f2',
            f3: Union[str, List[str]] = 'f3',
            vowel: str = 'vowel',
            rename: Union[str, dict] = None,
            groupby: Union[str, List[str]] = None,
            **kwargs):
        super().__init__(
            f1=f1 or 'f1',
            f2=f2 or 'f2',
            f3=f3 or 'f3',
            vowel=vowel,
            rename=rename,
            **kwargs)

    def _norm(self, df):
        f1, f2, f3 = self.params['f1'], self.params['f2'], self.params['f3']
        vowel = self.params['vowel']

        bootstrap_df = df[[f1, f2, vowel]].groupby(vowel).mean()
        beta = bootstrap_df.values

        # Normalize
        df[[f1, f2]] = df[[f1, f2]].div(
            np.cbrt(df[[f1, f2, f3]].apply(np.prod, axis=1)), axis=0)

        # Bootstrap denormalization
        def _denorm(_vowel):
            _df = bootstrap_df.loc[_vowel, pd.IndexSlice[[f1, f2]]]
            return _df
        dnm_df = df.copy()
        dnm_df[[f1, f2]] = dnm_df[[f1, f2]].mul(dnm_df[vowel].apply(_denorm).values, axis=0)
        mu = dnm_df[[f1, f2, vowel]].groupby(vowel).mean().values
        sigma = dnm_df[[f1, f2, vowel]].groupby(vowel).std().values
        vowels = [group[0] for group in dnm_df.groupby(vowel)]
        del dnm_df

        # Actual denormalization
        def _test(_df):
            dnm = _df[[f1, f2]].values * beta
            distances = (((dnm - mu) / sigma) ** 2).sum(axis=1)
            index = np.argmin(distances)
            return pd.Series(dict(
                f1=dnm[index, 0],
                f2=dnm[index, 1],
                vowel=vowels[index]))

        df[[f1, f2, vowel]] = df[[f1, f2, vowel]].apply(_test, axis=1)
        return df


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
