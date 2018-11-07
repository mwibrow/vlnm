"""
Centroid normalizers
~~~~~~~~~~~~~~~~~~~~

Normalizers which make use of the speakers vowel centroid.
"""
import numpy as np

from vlnm.normalizers.speaker import SpeakerIntrinsicNormalizer


class WattFabriciusNormalizer(SpeakerIntrinsicNormalizer):
    r"""
    .. math::

        F_i^\prime = \frac{F_i}{S(F_i)}

    Where:

    .. math::

        S(F_j) = \frac{1}{3}\left(F_j^{/i/} + F_j^{/a/} + F_j^{/u^\prime/}\right)

    and

    .. math::

        F_1^{/u^\prime/} = F_2^{/u^\prime/} = F_1^{/i/}

    """
    required_columns = ['speaker', 'vowel', 'f1', 'f2']
    required_keywords = ['fleece', 'trap']
    groups = ['speaker']

    @staticmethod
    def get_apice_formants(df, apices, **kwargs):
        """Calculate the formants for the apices of the speakers vowel space."""
        formants = kwargs['formants']
        vowel = kwargs.get('vowel', 'vowel')
        apice_df = df[df[vowel].isin(apices)]
        grouped = apice_df.groupby(vowel)
        apices = grouped.agg({f: np.mean for f in formants})

        return apices

    @staticmethod
    def _norm(df, **kwargs):
        formants = kwargs['formants']
        f1 = kwargs.get('f1', 'f1')
        f2 = kwargs.get('f2', 'f2')
        trap = kwargs['trap']
        fleece = kwargs['fleece']
        apices = [trap, fleece]

        apice_df = WattFabriciusNormalizer.get_apice_formants(
            df, apices, **kwargs)
        apice_df.loc['goose'] = apice_df.loc[fleece]
        apice_df.loc['goose', f2] = apice_df.loc[fleece, f1]
        centroids = apice_df.mean(axis=0)
        df[formants] /= centroids

        return df

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

    @staticmethod
    def _norm(df, **kwargs):
        formants = kwargs['formants']
        f1 = kwargs.get('f1', 'f1')
        f2 = kwargs.get('f2', 'f2')
        trap = kwargs['trap']
        fleece = kwargs['fleece']
        apices = [trap, fleece]

        apice_df = WattFabriciusNormalizer.get_apice_formants(
            df, apices, **kwargs)
        apice_df.loc['goose'] = apice_df.loc[fleece]
        apice_df.loc['goose', f2] = apice_df.loc[fleece, f1]

        def _means(series):
            if series.name == f2:
                return series[[fleece, 'goose']].mean()
            return series.mean()

        centroids = apice_df.apply(_means)
        df[formants] /= centroids

        return df


class WattFabricius3Normalizer(WattFabricius2Normalizer):
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

    @staticmethod
    def _norm(df, **kwargs):
        formants = kwargs['formants']
        trap = kwargs['trap']
        fleece = kwargs['fleece']
        apices = [trap, fleece]

        apice_df = WattFabriciusNormalizer.get_apice_formants(
            df, apices, **kwargs)
        apice_df.loc['goose'] = apice_df.min(axis=0)
        centroids = apice_df.mean(axis=0)
        df[formants] /= centroids

        return df


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

    @staticmethod
    def _norm(df, **kwargs):
        formants = kwargs['formants']
        apices = kwargs['apices']

        apice_df = BighamNormalizer.get_apice_formants(
            df, apices, **kwargs)
        centroids = apice_df.mean(axis=0)
        # X /= Y / Z <=> X = X / Y * Z
        df[formants] /= centroids / 100

        return df


class SchwaNormalizer(WattFabriciusNormalizer):
    r"""
    .. math::

        F_i^\prime = \frac{F_i}{F_{i[/ə/]}} - 1

    """
    required_columns = ['speaker', 'vowel']
    required_keywords = ['schwa']

    @staticmethod
    def _norm(df, **kwargs):
        formants = kwargs['formants']
        schwa = kwargs['schwa']

        apice_df = SchwaNormalizer.get_apice_formants(df, [schwa], **kwargs)
        centroids = apice_df.mean(axis=0)
        df[formants] = df[formants] / centroids - 1

        return df
