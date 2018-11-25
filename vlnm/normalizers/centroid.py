"""
Centroid normalizers
~~~~~~~~~~~~~~~~~~~~

Centroid normalizers are speaker intrinsic normalizers
which calculate the centroid of a speaker's vowel space
and use this to normalize the formant data.
"""

from typing import Any, Dict, List

import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull

from ..docstrings import docstring
from . import register_class
from .speaker import SpeakerIntrinsicNormalizer

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

def get_apice_formants(
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
        The columns of the data-frame will contain the formant labels
        and the index will contain the apice labels.

    """
    vowels = list(apices.values())
    vowels_df = df[df[vowel].isin(vowels)]
    grouped = vowels_df.groupby(vowel)

    def _agg(agg_df):
        names = {f: agg_df[f].mean() for f in formants}
        return pd.Series(names, index=formants)

    apice_df = grouped.agg(_agg)[formants]
    apice_df.sort_index(inplace=True)

    return apice_df


class CentroidNormalizer(SpeakerIntrinsicNormalizer):
    """Base class for centroid based normalizers."""

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
        apice_df = get_apice_formants(df, apices, vowel, formants)
        centroid = apice_df.mean(axis=0)
        return centroid


    def _norm(self, df):
        centroid = self.get_centroid(df, **self.params)
        formants = self.params['formants']
        df[formants] /= centroid
        return df

@docstring
class ConvexHullNormalizer(CentroidNormalizer):
    r"""Normalize using the barycenter of the speakers vowel space.

    The convex hull normalizer establishes the speaker's vowel
    space by calulating the `convex hull` :citep:`e.g., {% graham_yao_1983 %}`
    from the mean formants for `all` the speaker's vowels,
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


@register_class('wattfab')
class WattFabriciusNormalizer(CentroidNormalizer):
    r"""Normalize vowels according to :citet:`watt_fabricius_2002`.

    The :class:`WattFabriciusNormalizer` normalizes vowel data
    by dividing the componet formants for a vowel by a
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

    Example
    -------

    .. console::
        :code-only:

        >>> import pandas as pd
        >>> from vlnm import WattFabriciusNormalizer
        >>> normalizer = WattFabriciusNormalizer()
        >>> df = pd.read_csv('vowel_data.csv')
        >>> norm_df = normalizer(df, fleece='i:', trap='a')

    """
    config = dict(
        columns=['speaker', 'vowel', 'f1', 'f2'],
        keywords=['fleece', 'trap']
    )

    @staticmethod
    def get_centroid(df, apices=None, **kwargs):
        apices = apices or dict(fleece='fleece', trap='trap')
        formants = kwargs.get('formants', ['f1', 'f2'])
        vowel = kwargs.get('vowel', 'vowel')
        f1 = kwargs.get('f1', 'f1')
        f2 = kwargs.get('f2', 'f2')

        fleece = apices['fleece']
        apice_df = get_apice_formants(df, apices, vowel, formants)
        apice_df.loc['goose'] = apice_df.loc[fleece]
        apice_df.loc['goose', f2] = apice_df.loc[fleece, f1]
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

        .. console::
            :code-only:

            normalizer = WattFabriciousNormalizer()
            normalizer(df)
            # Same as
            normalizer.normalize(df)

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

WattFabricius1Normalizer = WattFabriciusNormalizer


@register_class('wattfab2')
class WattFabricius2Normalizer(WattFabriciusNormalizer):
    r"""
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
        keywords=['fleece', 'trap']
    )

    @staticmethod
    def get_centroid(df, apices=None, **kwargs):
        apices = apices or dict(fleece='fleece', trap='trap')
        formants = kwargs.get('formants', ['f1', 'f2'])
        vowel = kwargs.get('vowel', 'vowel')

        f1 = kwargs.get('f1', 'f1')
        f2 = kwargs.get('f2', 'f2')
        fleece = apices['fleece']
        apice_df = get_apice_formants(df, apices, vowel, formants)
        apice_df.loc['goose'] = apice_df.loc[fleece]
        apice_df.loc['goose', f2] = apice_df.loc[fleece, f1]

        def _means(series):
            if series.name == f2:
                return series[[fleece, 'goose']].mean()
            return series.mean()

        centroid = apice_df.apply(_means)
        return centroid


@register_class('wattfab3')
class WattFabricius3Normalizer(WattFabriciusNormalizer):
    r"""
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
        apice_df = get_apice_formants(df, apices or {}, vowel, formants)

        def _agg(agg_df):
            names = {f: agg_df[f].mean() for f in formants}
            return pd.Series(names, index=formants)

        # Minimum mean of all vowels (same as minimum mean of point vowels)
        apice_df.loc['goose'] = df.groupby(vowel).apply(_agg).min(axis=0)

        centroid = apice_df.mean(axis=0)
        return centroid


@register_class('bigham')
class BighamNormalizer(CentroidNormalizer):
    r"""

    Normalise vowels according to :citet:`bigham_2008`.

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

    .. console::
        :code-only:

        import pandas as pd
        from vlnm import BighamNormalizer
        apices=dict(
            kit='hid',
            goose='whod',
            fleece='heed',
            start='heart',
            thought='hoard',
            trap='had')
        normalizer = BighamNormalizer(apices)
        df = pd.read_csv('hawkins_midgely_2005.csv')
        df_norm = normalizer(df)

        df_norm.head()

    """
    config = dict(
        keywords=['apices', 'f1', 'f2'],
        columns=['speaker', 'vowel', 'f1', 'f2'],
        options=dict(
            apices=dict(
            kit='kit',
            goose='goose',
            fleece='fleece',
            start='start',
            thought='thought',
            trap='trap'))
    )

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

    @staticmethod
    def get_centroid(
            df: pd.DataFrame,
            apices: Dict[str, str] = None, **kwargs):

        f1 = kwargs.get('f1')
        f2 = kwargs.get('f2')
        formants = [f1, f2]
        vowel = kwargs.get('vowel')
        apice_df = get_apice_formants(df, apices, vowel, formants)

        centroid_df = apice_df.copy()

        kit, goose, fleece, start, thought = (
            apices['kit'], apices['goose'], apices['fleece'],
            apices['start'], apices['thought'])

        centroid_df.loc[fleece, f1] = centroid_df.loc[kit, f1]
        centroid_df.loc[goose, f1] = centroid_df.loc[fleece, f1]
        centroid_df.loc[start] = centroid_df.loc[[start, thought]].mean(axis=0)

        centroid_df.drop([kit, thought], axis=0, inplace=True)

        centroid = apice_df.mean(axis=0)
        return centroid

    def _keyword_default(self, keyword: str, df: pd.DataFrame=None) -> Any:
        if keyword == 'apices':
            lexical_set = ['kit', 'goose', 'fleece', 'start', 'thought', 'trap']
            return {key: key for key in lexical_set}
        return super()._keyword_default(keyword, df=df)


@register_class('schwa')
class SchwaNormalizer(CentroidNormalizer):
    r"""
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
