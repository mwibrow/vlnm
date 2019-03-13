"""
Centroid normalizers
~~~~~~~~~~~~~~~~~~~~

Centroid normalizers are speaker intrinsic normalizers
which calculate the centroid (i.e., geometric center)
of a speaker's vowel space
and use this to normalize the formant data by
divided the formants for each vowel by the
correspoinding formant of the centroid.
"""

from typing import Any, Dict, List

import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull

from ..docstrings import docstring
from .base import classify, register, FormantsNormalizer, FxNormalizer
from .speaker import SpeakerNormalizer

LEXICAL_SET = [
    'kit',
    'dress',
    'trap',
    'lot',
    'strut',
    'foot',
    'bath',
    'cloth',
    'nurse',
    'fleece',
    'face',
    'palm',
    'thought',
    'goat',
    'goose',
    'price',
    'choice',
    'mouth',
    'near',
    'square',
    'start',
    'north',
    'force',
    'cure',
    'happy',
    'letter',
    'comma'
]


def _get_apice_formants(
        df: pd.DataFrame,
        apices: Dict[str, str],
        vowel: str,
        formants: List[str],
        **_kwargs) -> pd.DataFrame:
    r"""Helper function for extracting formant means for vowel space apices.

    Parameters
    ----------
    df :
        The formant data for single speaker.
    apices :
        A dictionary whose keys are the lexical set keywords for apices
        of the vowel space, and whose values are the vowel labels in
        the DataFrame.
    vowel :
        The column in the data-frame containing vowel labels
    formants :
        A list of columns in the data-frame containing the formant data.

    Returns
    -------
    :obj:`DataFrame`
        A data-frame containing the mean formant values for each apice
        in the speakers vowel space.
        The columns of the data-frame will contain the formant means
        and the index will contain the apice labels.

    """
    if not apices:
        apices = {key: key for key in df[vowel].unique()}
    vowels = list(apices.values())
    vowels_df = df[df[vowel].isin(vowels)]
    grouped = vowels_df.groupby(vowel)

    def _agg(agg_df):
        names = {f: agg_df[f].mean() for f in formants}
        return pd.Series(names, index=formants)

    apice_df = grouped.agg(_agg)[formants]

    # Rename the index using the apice map keys.
    secipa = {value: key for key, value in apices.items()}
    apice_df.index = apice_df.index.map(secipa)

    return apice_df


@docstring
@register('centroid')
@classify(vowel='extrinsic', formant='intrinsic', speaker='intrinsic')
class CentroidNormalizer(SpeakerNormalizer):
    """Normalize using the geometric center of the speakers entire vowel space.

    Parameters
    ----------
    {% formants %}
    {% speaker %}
    {% vowel %}
    apices:
        List of vowel labels corresponding to each apex of the speakers vowel space.
    {% rename %}
    """

    config = dict(
        columns=['speaker', 'vowel'],
        keywords=['speaker', 'vowel', 'apices'])

    @staticmethod
    def get_centroid(
            df: pd.DataFrame,
            apices: Dict[str, str] = None,
            **kwargs):  # pylint: disable=missing-docstring
        apices = apices or {}
        formants = kwargs.get('formants', [])
        vowel = kwargs.get('vowel', 'vowel')
        apice_df = _get_apice_formants(df, apices, vowel, formants)
        centroid = apice_df.mean(axis=0)
        return centroid

    def _norm(self, df):
        centroid = self.get_centroid(df, **self.params)
        formants = self.params['formants']
        df[formants] /= centroid
        return df


@docstring
@register('convex-hull')
@classify(vowel='extrinsic', formant='intrinsic', speaker='intrinsic')
class ConvexHullNormalizer(CentroidNormalizer, FormantsNormalizer):
    r"""Normalize using the geometric center of the convex hull enclosing the speakers vowel space.

    The convex hull normalizer establishes the speaker's vowel
    space by calulating the `convex hull` :citep:`e.g., {% graham_yao_1983 %}`
    from the mean formants for `each` the speaker's vowels,
    and uses the barycenter of the points
    that make-up the hull to normalize the formant data.

    .. math::

        F_i^\prime = \frac{F_i}{S_i}

    where

    .. math::

        S_i = \frac{1}{|H|}\sum_{h\in H}F_i(h)

    Where :math:`H` is the the set of vowels which form the convex
    hull of the vowel space and :math:`F_i(h)` is the :math:`i^{th}`
    formant of vowel :math:`h`.

    Parameters
    ----------

    {% formants %}
    {% speaker %}
    {% vowel %}
    {% kwargs %}

    Returns
    -------
    {{normalized_data}}

    """

    def __init__(
            self, formants=None, speaker='speaker', vowel='vowel', **kwargs):
        super().__init__(
            formants=formants, speaker=speaker, vowel=vowel, **kwargs)

    @staticmethod
    def get_centroid(df, apices=None, **kwargs):  # pylint: disable=missing-docstring
        vowel = kwargs.get('vowel')
        formants = kwargs.get('formants')
        subset = [vowel]
        subset.extend(formants)
        means = df[subset].groupby(vowel).mean().as_matrix()

        hull = ConvexHull(means)
        points = np.array([means[vertex] for vertex in hull.vertices])

        centroid = points.mean(axis=1)
        return centroid


@register('wattfab1')
@classify(vowel='extrinsic', formant='intrinsic', speaker='intrinsic')
class WattFabricius1Normalizer(CentroidNormalizer, FxNormalizer):
    r"""Normalize vowels according to :citet:`watt_fabricius_2002`.

    Formant data is normalized by
    by dividing the component formants for a vowel by a
    the components of a centroid calculated
    from the :math:`F_1` and :math:`F_2` data for the
    :smallcaps:`fleece`, :smallcaps:`trap` and :smallcaps:`goose` vowels, with
    the formants for the :smallcaps:`goose` vowel derived
    from the other vowels by setting
    :math:`F_1` and :math:`F_2` to the :math:`F_1`
    of the :smallcaps:`fleece` vowel.

    .. math::

        F_i^\prime = \frac{F_i}{S(F_i)}

    Where:

    .. math::

        S(F_j) = \frac{1}{3}\left
            (F_j^{[i]} + F_j^{[a]} + F_j^{[u^\prime]}
        \right)

    and

    .. math::

        F_1^{[u^\prime]} = F_2^{[u^\prime]} = F_1^{[i]}

    with :math:`[i]`, :math:`[a]`, and :math:`[u^\prime]` indicating
    the :smallcaps:`fleece`, :smallcaps:`trap`
    and (derived) :smallcaps:`goose` vowels, respectively.



    """
    config = dict(
        columns=['speaker', 'vowel', 'f1', 'f2'],
        keywords=['apices']
    )

    @staticmethod
    def get_centroid(df, apices=None, **kwargs):
        apices = apices or dict(fleece='fleece', trap='trap')
        vowel = kwargs.get('vowel', 'vowel')
        f1 = kwargs.get('f1', 'f1')
        f2 = kwargs.get('f2', 'f2')
        formants = [f1, f2]
        apice_df = _get_apice_formants(df, apices, vowel, formants)
        apice_df.loc['goose'] = apice_df.loc['fleece']
        apice_df.loc['goose', f2] = apice_df.loc['fleece', f1]
        centroid = apice_df.mean(axis=0)
        return centroid

    def normalize(
            self,
            df: pd.DataFrame,
            apices: Dict[str, str] = None,
            **kwargs) -> pd.DataFrame:
        """
        Normalize a dataframe.
        Note that a :class:`WattFabriciusNormalizer` instance is `callable`,
        and the call is forwarded to this method.



        Parameters
        ----------

        df : :class:`pandas.DataFrame`
            Formant data.

        apices
        fleece : :obj:`str`
            Vowel label for the :smallcaps:`fleece` vowel.

        trap : :obj:`str`
            Vowel label for the :smallcaps:`trap` vowel.

        **kwargs
            Other keyword arguments passed on to the parent class.

        Returns
        -------
        :class:`pandas.DataFrame`
            A with the normalized formants.
        """
        apices = apices or dict(fleece='fleece', trap='trap')
        return super().normalize(df, apices=apices, **kwargs)


WattFabriciusNormalizer = WattFabricius1Normalizer


@register('wattfab2')
@classify(vowel='extrinsic', formant='intrinsic', speaker='intrinsic')
class WattFabricius2Normalizer(WattFabricius1Normalizer):
    r"""
    Second centroid normalizer described in :citet:`watt_fabricius_2002`.

    .. math::

        F_i^\prime = \frac{F_i}{S(F_i)}

    Where:

    .. math::

        S(F_j) = \begin{cases}
            \frac{1}{2}\left(F_j^{[i]} + F_j^{[u^\prime]}\right)
            & \text{when } j = 2
            \\
            \frac{1}{3}\left(F_j^{[i]} + F_j^{[a]} + F_j^{[u^\prime]}\right)
            & \text{otherwise}
        \end{cases}

    and

    .. math::

        F_1^{[u^\prime]} = F_2^{[u^\prime]} = F_1^{[i]}

    """

    config = dict(
        columns=['speaker', 'vowel', 'f1', 'f2'],
        keywords=['apices']
    )

    @staticmethod
    def get_centroid(df, apices=None, **kwargs):
        apices = apices or dict(fleece='fleece', trap='trap')
        vowel = kwargs.get('vowel', 'vowel')
        f1 = kwargs.get('f1', 'f1')
        f2 = kwargs.get('f2', 'f2')

        formants = [f1, f2]

        apice_df = _get_apice_formants(df, apices, vowel, formants)
        apice_df.loc['goose'] = apice_df.loc['fleece']
        apice_df.loc['goose', f2] = apice_df.loc['fleece', f1]

        def _means(series):
            if series.name == f2:
                return series[['fleece', 'goose']].mean()
            return series.mean()

        centroid = apice_df.apply(_means)
        return centroid


@register('wattfab3')
@classify(vowel='extrinsic', formant='intrinsic', speaker='intrinsic')
class WattFabricius3Normalizer(WattFabricius1Normalizer):
    r"""
    Third centroid normalizer described in :citet:`watt_fabricius_2002`.

    .. math::

        F_i^\prime = \frac{F_i}{S(F_i)}

    Where:

    .. math::

        S(F_j) = \begin{cases}
            \frac{1}{2}\left(F_j^{[i]} + F_j^{[u^\prime]}\right)
            & \text{when } j = 2
            \\
            \frac{1}{3}\left(F_j^{[i]} + F_j^{[a]} + F_j^{[u^\prime]}\right)
            & \text{otherwise}
        \end{cases}

    and

    .. math::

        F_j^{[u^\prime]} = \underset{\rho}{\text{argmin}}\mbox{ }\mu_{F_k^{/\rho \in P/}}

    where :math:`P` is the set of point vowels.
    """

    @staticmethod
    def get_centroid(df, apices=None, **kwargs):
        formants = kwargs.get('formants')
        vowel = kwargs.get('vowel', 'vowel')
        apice_df = _get_apice_formants(df, apices or {}, vowel, formants)

        def _agg(agg_df):
            names = {f: agg_df[f].mean() for f in formants}
            return pd.Series(names, index=formants)

        # Minimum mean of all vowels (same as minimum mean of point vowels)
        apice_df.loc['goose'] = df.groupby(vowel).apply(_agg).min(axis=0)

        centroid = apice_df.mean(axis=0)
        return centroid


@register('bigham')
@classify(vowel='extrinsic', formant='intrinsic', speaker='intrinsic')
class BighamNormalizer(CentroidNormalizer, FxNormalizer):
    r"""
    Centroid normalizer using the centroid calculated according to :citet:`bigham_2008`.

    :citet:`bigham_2008` adapts :citet:`watt_fabricius_2002`
    to calculate a barycentric centroid from a trapzeoid
    constructed using the vowels
    :ipa:`[i^\prime]`, :ipa:`[u^\prime]`
    :ipa:`[ɑ^\prime]`, and :ipa:`[æ^\prime]`
    derived as shown below:

    .. list-table:: Construction of derived vowels
        :header-rows: 1
        :align: center
        :class: centered

        * - vowel
          - F1
          - F2
        * - :ipa:`[i^\prime]`
          - :math:`F_1^{[ɪ]}`
          - :math:`F_2^{[i]}`
        * - :ipa:`[u^\prime]`
          - :math:`F_1^{[i]}`
          - :math:`F_2^{[u]}`
        * - :ipa:`[ɑ^\prime]`
          - :math:`\frac{1}{2}(F_1^{[ɑ]} + F_1^{[ɔ]})`
          - :math:`\frac{1}{2}(F_2^{[ɑ]} + F_2^{[ɔ]})`
        * - :ipa:`[æ^\prime]`
          - :math:`F_1^{[æ]}`
          - :math:`F_2^{[æ]}`

    Then the formants are normalized as follows:

    .. math::

        F_i^\prime = \frac{F_i}{S(F_i)}

    Where:

    .. math::

        S(F_i) = \frac{1}{4}
            \left(
                F_i^{[i^\prime]} +
                F_i^{[u^\prime]} +
                F_i^{[ɑ^\prime]} +
                F_i^{[æ^\prime]}
            \right)



    Parameters
    ----------
    f1 : :obj:`str`
        The DataFrame column which contains the :math:`F_1` data.
        If not given (or overridden in the `normalize` method)
        defaults to ``'f1'``.

    f2 : :obj:`str`
        The DataFrame column which contains the :math:`F_2` data.
        If not given (or overridden in the `normalize` method)
        defaults to ``'f2'``.

    speaker: :obj:`str`
        The DataFrame column which contains the speaker labels.
        If not given (or overridden in the `normalize` method)
        defaults to ``'speaker'``.

    vowel: :obj:`str`
        The DataFrame column which contains the vowel labels.
        If not given (or overridden in the `normalize` method)
        defaults to ``'vowel'``.

    apices : :obj:`dict`
        A dictionary specifying labels for the required vowels
        to construct the centroid (shown in the table above).
        The keys for the dictionary should be from the
        lexical set keywords (see table below)
        and *all* keys need to be specified.

        If this parameter is omitted, the normalizer will assume that the vowels
        are already labeled according to the lexical set keywords
        taken from :citet:`wells_1982`:


    .. list-table:: Lexical set keywords with corresponding dictionary keys
        :header-rows: 1
        :align: center
        :class: centered

        * - Keyword
          - SSBE vowel
          - Dictionary key
        * - :smallcaps:`kit`
          - :ipa:`ɪ`
          - ``kit``
        * - :smallcaps:`goose`
          - :ipa:`u`
          - ``goose``
        * - :smallcaps:`fleece`
          - :ipa:`i`
          - ``fleece``
        * - :smallcaps:`start`
          - :ipa:`ɑ`
          - ``fleece``
        * - :smallcaps:`thought`
          - :ipa:`ɔ`
          - ``thought``
        * - :smallcaps:`trap`
          - :ipa:`æ`
          - ``trap``

    kwargs :
        Other keyword arguments passed to the parent class.

    Returns
    -------
    `pandas.DataFrame`
        The normalized data.

    Example
    -------

    """
    config = dict(
        keywords=['apices', 'f1', 'f2'],
        columns=['speaker', 'vowel', 'f1', 'f2'],
        options={})

    def __init__(
            self,
            f1: str = 'f1',
            f2: str = 'f2',
            speaker: str = 'speaker',
            vowel: str = 'vowel',
            apices: Dict[str, str] = None,
            **kwargs):
        super().__init__(
            apices=apices, f1=f1, f2=f2,
            speaker=speaker, vowel=vowel, **kwargs)

    def normalize(
            self,
            df: pd.DataFrame,
            f1: 'str' = None,
            f2: 'str' = None,
            apices: Dict[str, str] = None,
            speaker: 'str' = None,
            vowel: 'str' = None,
            rename: 'str' = None,
            **_kwargs):
        return super().normalize(
            df, f1=f1, f2=f2, apices=apices,
            speaker=speaker, vowel=vowel, rename=rename)

    @staticmethod
    def get_centroid(
            df: pd.DataFrame,
            apices: Dict[str, str] = None, **kwargs):

        f1 = kwargs.get('f1')
        f2 = kwargs.get('f2')
        formants = [f1, f2]
        vowel = kwargs.get('vowel')
        apice_df = _get_apice_formants(df, apices, vowel, formants)

        centroid_df = apice_df.copy()

        centroid_df.loc['goose', f1] = centroid_df.loc['fleece', f1]
        centroid_df.loc['fleece', f1] = centroid_df.loc['kit', f1]
        centroid_df.loc['start'] = centroid_df.loc[
            ['start', 'thought']].mean(axis=0)

        centroid_df.drop(['kit', 'thought'], axis=0, inplace=True)
        centroid = centroid_df.mean(axis=0)
        return centroid

    def _keyword_default(self, keyword: str, df: pd.DataFrame = None) -> Any:
        if keyword == 'apices':
            lexical_set = ['kit', 'goose', 'fleece', 'start', 'thought', 'trap']
            return {key: key for key in lexical_set}
        return super()._keyword_default(keyword, df=df)


@register('schwa')
@classify(vowel='extrinsic', formant='intrinsic', speaker='intrinsic')
class SchwaNormalizer(CentroidNormalizer):
    r"""Centroid normalizer using formant data for [ə] as the centroid.

    .. math::

        F_i^\prime = \frac{F_i}{F_{i}^{[ə]}} - 1

    """
    config = dict(
        columns=['speaker', 'vowel'],
        keywords=['schwa']
    )

    def _normalize(self, df):
        schwa = self.options['schwa']
        self.options['apices'] = {'letter': schwa}
        return super()._normalize(df)

    def _norm(self, df):
        df = super()._norm(df)
        formants = self.params['formants']
        df[formants] -= 1.
        return df
