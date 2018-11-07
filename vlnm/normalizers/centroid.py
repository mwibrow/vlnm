"""
Centroid normalizers
~~~~~~~~~~~~~~~~~~~~

Normalizers which make use of the speakers vowel centroid.
"""
import numpy as np

from vlnm.normalizers.speaker import SpeakerIntrinsicNormalizer
from vlnm.decorators import (
    Columns,
    DocString,
    Keywords,
    Register)


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
    def get_apice_formants(df, **kwargs):
        """Calculate the centroid for the speaker."""
        formants = kwargs['formants']
        f1 = kwargs.get('f1', 'f1')
        f2 = kwargs.get('f2', 'f2')
        vowel = kwargs.get('vowel', 'vowel')
        trap = kwargs['trap']
        fleece = kwargs['fleece']

        vowels = [trap, fleece]
        apice_df = df[df[vowel].isin(vowels)]
        agg = {f: np.mean for f in formants}
        grouped = apice_df.groupby(vowel)

        apice_df = grouped.agg(agg)
        return apice_df

    @staticmethod
    def _norm(df, **kwargs):
        formants = kwargs['formants']
        f1 = kwargs.get('f1', 'f1')
        f2 = kwargs.get('f2', 'f2')
        vowel = kwargs.get('vowel', 'vowel')
        trap = kwargs['trap']
        fleece = kwargs['fleece']

        apice_df = WattFabriciusNormalizer.get_apice_formants(df, **kwargs)
        apice_df.loc['goose'] = apice_df.loc[fleece]
        apice_df.loc['goose', f2] = apice_df.loc[fleece, f1]

        centroids = apice_df.mean()
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
    def speaker_stats(df, **kwargs):  # pylint: disable=C0111
        super(
            WattFabricius2Normalizer,
            WattFabricius2Normalizer).speaker_stats(df, **kwargs)
        constants = kwargs['constants']

        f2 = kwargs.get('f2', 'f2')

        constants['{}_centroid'.format(f2)] = (
            constants['{}_fleece'.format(f2)] +
            constants['{}_goose'.format(f2)]) / 2


@DocString
@Columns(
    required=['speaker', 'vowel', 'f1', 'f2']
)
@Keywords(
    required=['point_vowels']
)
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
    def speaker_stats(df, **kwargs):  # pylint: disable=C0111
        constants = kwargs['constants']
        formants = kwargs['formants']
        f2 = kwargs.get('f2', 'f2')
        vowel = kwargs.get('vowel', 'vowel')
        trap = kwargs.get('trap', 'trap')
        fleece = kwargs.get('fleece', 'fleece')

        point_vowels = kwargs.get('point_vowels')

        for formant in formants:
            constants['{}_fleece'.format(formant)] = (
                df[df[vowel] == fleece][formant].mean())
            constants['{}_trap'.format(formant)] = (
                df[df[vowel] == trap][formant].mean())
            constants['{}_goose'.format(formant)] = (
                df[df[vowel].isin(point_vowels)].groupby(
                    vowel).apply(lambda x, i=formant: x[i].mean()).min()).min()

            constants['{}_centroid'.format(formant)] = (
                constants['{}_fleece'.format(formant)] +
                constants['{}_trap'.format(formant)] +
                constants['{}_goose'.format(formant)]) / 3

        constants['{}_centroid'.format(f2)] = (
            constants['{}_fleece'.format(f2)] +
            constants['{}_goose'.format(f2)]) / 2


@DocString
@Columns(
    required=['speaker', 'vowel']
)
@Keywords(
    required=['apices']
)
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
        vowel = kwargs.get('vowel', 'vowel')
        apices = kwargs['apices']

        apice_df = df[df[vowel].isin(apices)]
        agg = {f: np.mean for f in formants}
        grouped = apice_df.groupby(vowel, as_index=False)
        centroids = grouped.agg(agg)[formants].mean()

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
        vowel = kwargs.get('vowel', 'vowel')
        schwa = kwargs['schwa']
        for formant in formants:
            centroid = df[df[vowel] == schwa][formant].mean()
            df[formant] /= centroid
        return df
