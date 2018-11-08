"""
Centroid normalizers
~~~~~~~~~~~~~~~~~~~~

Centroid normalizers are speaker intrinsic normalizers
which calculate the centroid of a speaker's vowel space
and use this to normalize the formant data.
"""

import pandas as pd

from vlnm.normalizers.speaker import SpeakerIntrinsicNormalizer

class CentroidNormalizer(SpeakerIntrinsicNormalizer):
    """Base class for centroid based normalizers."""

    @staticmethod
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

    @classmethod
    def get_centroid(cls, df, apices, **kwargs):
        r"""Calculate the speakers centroid.

        Parameters
        ----------
        df : DataFrame
            The formant data for single speaker.
        apices : list
            A list of vowel labels denoting the apices of the vowel space.
        **kwargs
            Keyword arguments which are passed on to the class method
            `get_apice_formants`.
            Sub-classes of this class may override this method
            and use any other keywords passed.

        Returns
        -------
        :obj:`pandas.Series`
            Centroid data for each formant.
        """
        apice_df = cls.get_apice_formants(df, apices, **kwargs)
        centroid = apice_df.mean(axis=0)
        return centroid

    @classmethod
    def _norm(cls, df, **kwargs):
        formants = kwargs.get('formants')
        apices = kwargs.pop('apices', [])
        centroid = cls.get_centroid(df, apices, **kwargs)
        df[formants] /= centroid
        return df


class WattFabriciusNormalizer(CentroidNormalizer):
    r"""
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

    """
    required_columns = ['speaker', 'vowel', 'f1', 'f2']
    required_keywords = ['fleece', 'trap']

    def _normalize(self, df, groups=None, **kwargs):
        apices = kwargs.get('apices')
        if apices:
            return super()._normalize(df, groups=groups, **kwargs)
        trap = kwargs['trap']
        fleece = kwargs['fleece']
        return super()._normalize(
            df, apices=[trap, fleece], groups=groups, **kwargs)

    @classmethod
    def get_centroid(cls, df, apices, **kwargs):
        """Calculate the speakers centroid."""
        f1 = kwargs.get('f1', 'f1')
        f2 = kwargs.get('f2', 'f2')
        fleece = kwargs['fleece']

        apice_df = cls.get_apice_formants(
            df, apices, **kwargs)
        apice_df.loc['goose'] = apice_df.loc[fleece]
        apice_df.loc['goose', f2] = apice_df.loc[fleece, f1]
        centroid = apice_df.mean(axis=0)
        return centroid


WattFabricius1Normalizer = WattFabriciusNormalizer


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

    required_columns = ['speaker', 'vowel', 'f1', 'f2']
    required_keywords = ['fleece', 'trap']

    @classmethod
    def get_centroid(cls, df, apices, **kwargs):
        """Calculate the speakers centroid."""
        f1 = kwargs.get('f1', 'f1')
        f2 = kwargs.get('f2', 'f2')
        fleece = kwargs['fleece']

        apice_df = cls.get_apice_formants(
            df, apices, **kwargs)
        apice_df.loc['goose'] = apice_df.loc[fleece]
        apice_df.loc['goose', f2] = apice_df.loc[fleece, f1]

        def _means(series):
            if series.name == f2:
                return series[[fleece, 'goose']].mean()
            return series.mean()

        centroid = apice_df.apply(_means)
        return centroid


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

        F_j^{/u^\prime/} = \underset{\rho}{\text{argmin}} \mu_{F_k^{/\rho \in P/}}

    where :math:`P` is the set of point vowels.
    """

    @classmethod
    def get_centroid(cls, df, apices, **kwargs):
        """Calculate the speakers centroid."""
        apice_df = cls.get_apice_formants(
            df, apices, **kwargs)
        apice_df.loc['goose'] = apice_df.min(axis=0)

        centroid = apice_df.mean(axis=0)
        return centroid


class BighamNormalizer(WattFabriciusNormalizer):
    r"""

    Normalise vowels according to Bigham 2006:

    .. math::

        F_i^\prime = \frac{F_i}{S(F_i)}

    Where:

    .. math::

        S(F_i) = \frac{1}{|q|}\sum_{q\in Q}F_i

    Where :math:`Q` is the set of vowels at the apices
    of the speakers vowel space.

    """
    required_columns = ['speaker', 'vowel']
    required_keyowrds = ['apices']


class SchwaNormalizer(CentroidNormalizer):
    r"""
    .. math::

        F_i^\prime = \frac{F_i}{F_{i[/ə/]}} - 1

    """
    required_columns = ['speaker', 'vowel']
    required_keywords = ['schwa']

    def _normalize(self, df, groups=None, **kwargs):
        schwa = kwargs['schwa']
        kwargs['apices'] = [schwa]
        return super()._normalize(df, groups=groups, **kwargs)

    @classmethod
    def _norm(cls, df, **kwargs):
        df = cls._norm(cls, df, **kwargs)
        df -= 1
        return df
