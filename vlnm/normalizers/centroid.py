"""
Centroid normalizers
~~~~~~~~~~~~~~~~~~~~

Centroid normalizers are speaker intrinsic normalizers
which calculate the centroid of a speaker's vowel space
and use this to normalize the formant data.
"""

import pandas as pd

from . import register_class
from .speaker import SpeakerIntrinsicNormalizer


def get_apice_formants(df, apices, **kwargs):
    r"""Calculate the formants for the apices of the speakers vowel space.

    Parameters
    ----------
    df : DataFrame
        The formant data for single speaker.
    apices : list
        A list of vowel labels denoting the apices of the vowel space.
    **kwargs
        Keyword arguments.

    Keyword arguments
    -----------------
    formants : list
        A list of columns in the data-frame containing the formant data.
    vowel : :obj:`str`, optional
        The column in the data-frame containing vowel labels

    Returns
    -------
    :obj:`DataFrame`
        A data-frame containing the mean formant values for each apice
        in the speakers vowel space.
        The columns of the data-frame will contain the formant labels
        and the index will contain the apice labels.

    """
    formants = kwargs['formants']
    vowel = kwargs.get('vowel', 'vowel')
    vowels_df = df[df[vowel].isin(apices)]
    grouped = vowels_df.groupby(vowel)

    def _agg(agg_df):
        names = {f: agg_df[f].mean() for f in formants}
        return pd.Series(names, index=formants)

    apice_df = grouped.agg(_agg)[formants]
    return apice_df


class CentroidNormalizer(SpeakerIntrinsicNormalizer):
    """Base class for centroid based normalizers."""

    required_columns = ['speaker', 'vowel']


    @staticmethod
    def get_centroid(df, apices=None, **kwargs):  # pylint: disable=missing-docstring
        apices = apices or []
        apice_df = get_apice_formants(df, apices, **kwargs)
        centroid = apice_df.mean(axis=0)
        return centroid


    def _norm(self, df):
        centroid = self.get_centroid(df, **self.params)
        formants = self.params['formants']
        df[formants] /= centroid
        return df


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
            (F_j^{/i/} + F_j^{/a/} + F_j^{/u^\prime/}
        \right)

    and

    .. math::

        F_1^{/u^\prime/} = F_2^{/u^\prime/} = F_1^{/i/}

    with :math:`/i/`, :math:`/a/`, and :math:`/u^\prime/` indicating
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
        apices = apices or []
        f1 = kwargs.get('f1', 'f1')
        f2 = kwargs.get('f2', 'f2')
        fleece = kwargs['fleece']
        trap = kwargs['trap']
        apices = apices or [fleece, trap]
        apice_df = get_apice_formants(df, apices, **kwargs)
        apice_df.loc['goose'] = apice_df.loc[fleece]
        apice_df.loc['goose', f2] = apice_df.loc[fleece, f1]
        centroid = apice_df.mean(axis=0)
        return centroid

    def normalize(self, df, fleece='fleece', trap='trap', **kwargs):
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
        return super().normalize(df, fleece=fleece, trap=trap, **kwargs)

WattFabricius1Normalizer = WattFabriciusNormalizer


@register_class('wattfab2')
class WattFabricius2Normalizer(WattFabriciusNormalizer):
    r"""
    .. math::

        F_i^\prime = \frac{F_i}{S(F_i)}

    Where:

    .. math::

        S(F_j) = \begin{cases}
            \frac{1}{2}\left(F_j^{/i/} + F_j^{/u^\prime/}\right)
            & \text{when } j = 2
            \\
            \frac{1}{3}\left(F_j^{/i/} + F_j^{/a/} + F_j^{/u^\prime/}\right)
            & \text{otherwise}
        \end{cases}

    and

    .. math::

        F_1^{/u^\prime/} = F_2^{/u^\prime/} = F_1^{/i/}

    """

    config = dict(
        columns=['speaker', 'vowel', 'f1', 'f2'],
        keywords=['fleece', 'trap']
    )

    @staticmethod
    def get_centroid(df, apices=None, **kwargs):
        f1 = kwargs.get('f1', 'f1')
        f2 = kwargs.get('f2', 'f2')
        fleece = kwargs['fleece']
        trap = kwargs['trap']
        apices = apices or [fleece, trap]
        apice_df = get_apice_formants(df, apices, **kwargs)
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
            \frac{1}{2}\left(F_j^{/i/} + F_j^{/u^\prime/}\right)
            & \text{when } j = 2
            \\
            \frac{1}{3}\left(F_j^{/i/} + F_j^{/a/} + F_j^{/u^\prime/}\right)
            & \text{otherwise}
        \end{cases}

    and

    .. math::

        F_j^{/u^\prime/} = \underset{\rho}{\text{argmin}}\mbox{ }\mu_{F_k^{/\rho \in P/}}

    where :math:`P` is the set of point vowels.
    """

    @staticmethod
    def get_centroid(df, apices=None, **kwargs):
        apice_df = get_apice_formants(df, apices or [], **kwargs)

        formants = kwargs.get('formants')
        vowel = kwargs.get('vowel', 'vowel')
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

    .. list-table::
        :header-rows: 1
        :align: center

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

    .. list-table::
        :header-rows: 1
        :align: center

        * - keyword
          - SSE vowel
        * - :smallcaps:`kit`
          - :ipa:`ɪ`
        * - :smallcaps:`goose`
          - :ipa:`u`
        * - :smallcaps:`fleece`
          - :ipa:`i`
        * - :smallcaps:`start`
          - :ipa:`ɑ`
        * - :smallcaps:`thought`
          - :ipa:`ɔ`
        * - :smallcaps:`trap`
          - :ipa:`æ`

    Parameters
    ----------

    apices : :obj:`dict`
        A dictionary specifying labels for the required vowels
        to construct the centroid (shown in the table above).
        The keys for the dictionary should be from the
        lexical set keywords :smallcaps:`kit`,
        :smallcaps:`goose`, :smallcaps:`fleece`, :smallcaps:`start`,
        :smallcaps:`thought`, and :smallcaps:`trap`,
        and *all* keys need to be specified.
        If this parameter is omitted, the normalizer will assume that the vowels
        are already labeled according by the lexical set keywords.



    """
    config = dict(
        keywords=['apices'],
        columns=['speaker', 'vowel']
    )

    @staticmethod
    def get_centroid(df, apices=None, **kwargs):
        apice_df = get_apice_formants(
            df, list((apices or {}).keys()), **kwargs)

        formants = kwargs.get('formants')
        vowel = kwargs.get('vowel', 'vowel')
        def _agg(agg_df):
            names = {f: agg_df[f].mean() for f in formants}
            return pd.Series(names, index=formants)
        # Minimum mean of all vowels (same as minimum mean of point vowels)
        apice_df.loc['goose'] = df.groupby(vowel).apply(_agg).min(axis=0)

        centroid = apice_df.mean(axis=0)
        return centroid

    def _keyword_default(self, keyword, df=None):
        if keyword == 'apices':
            lexical_set = ['kit', 'goose', 'fleece', 'start', 'thought', 'trap']
            return {key: key for key in lexical_set}
        return super()._keyword_default(keyword, df=df)


@register_class('schwa')
class SchwaNormalizer(CentroidNormalizer):
    r"""
    .. math::

        F_i^\prime = \frac{F_i}{F_{i[/ə/]}} - 1

    """
    config = dict(
        columns=['speaker', 'vowel'],
        keywords=['schwa']
    )

    def _normalize(self, df):
        schwa = self.options['schwa']
        self.options['apices'] = [schwa]
        return super()._normalize(df)

    def _norm(self, df):
        df = super()._norm(df)
        formants = self.params['formants']
        df[formants] -= 1.
        return df
