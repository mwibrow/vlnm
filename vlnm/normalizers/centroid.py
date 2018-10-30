"""
Centroid normalizers
~~~~~~~~~~~~~~~~~~~~

Normalizers which make use of the speakers vowel centroid.
"""

from vlnm.normalizers.base import VowelNormalizer
from vlnm.decorators import (
    Columns,
    DocString,
    Keywords,
    Register)

@Register('wattfabb')
@DocString
@Columns(
    required=['speaker', 'vowel', 'f1', 'f2']
)
@Keywords(
    required=['fleece', 'trap']
)
class WattFabriciusNormalizer(VowelNormalizer):
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
    def __init__(self, **kwargs):
        super(WattFabriciusNormalizer, self).__init__(**kwargs)
        self.actions.update(
            speaker=self.speaker_stats
        )
        self.groups = ['speaker']

    @staticmethod
    def speaker_stats(df, **kwargs):  # pylint: disable=C0111
        constants = kwargs['constants']
        formants = kwargs['formants']
        f1 = kwargs.get('f1', 'f1')
        f2 = kwargs.get('f2', 'f2')
        vowel = kwargs.get('vowel', 'vowel')
        trap = kwargs['trap']
        fleece = kwargs['fleece']

        for formant in formants:
            constants['{}_fleece'.format(formant)] = (
                df[df[vowel] == fleece][formant].mean())
            constants['{}_trap'.format(formant)] = (
                df[df[vowel] == trap][formant].mean())
            constants['{}_goose'.format(formant)] = (
                constants['{}_fleece'.format(formant)])

        constants['{}_goose'.format(f1)] = (
            constants['{}_fleece'.format(f1)])
        constants['{}_goose'.format(f2)] = (
            constants['{}_fleece'.format(f1)])

        for formant in formants:
            constants['{}_centroid'.format(formant)] = (
                constants['{}_fleece'.format(formant)] +
                constants['{}_trap'.format(formant)] +
                constants['{}_goose'.format(formant)]) / 3

    def _norm(self, df, **kwargs):
        constants = kwargs['constants']
        formants = kwargs['formants']

        for formant in formants:
            centroid = constants['{}_centroid'.format(formant)]
            df[formant] /= centroid
        return df

WaltFabricious1Normalizer = WattFabriciusNormalizer


@DocString
@Columns(
    required=['speaker', 'vowel', 'f1', 'f2']
)
@Keywords(
    required=['fleece', 'trap']
)
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
    of the speakers vowel quadrilateral.


    """
    def __init__(self, **kwargs):
        super(BighamNormalizer, self).__init__(**kwargs)
        self.actions.update(
            speaker=self.speaker_stats
        )
        self.groups = ['speaker']

    @staticmethod
    def speaker_stats(df, **kwargs):  # pylint: disable=C0111
        constants = kwargs['constants']
        formants = kwargs['formants']
        vowel = kwargs.get('vowel', 'vowel')
        apices = kwargs['apices']

        for formant in formants:
            for apice in apices:
                constants['{}_{}'.format(formant, apice)] = (
                    df[df[vowel] == apice][formant].mean())


            constants['{}_centroid'.format(formant)] = (
                sum(constants['{}_{}'.format(formant, apice)]
                    for apice in apices) / len(apices))

    def _norm(self, df, **kwargs):
        formants = kwargs['formants']
        df = super(BighamNormalizer, self)._norm(df, **kwargs)
        for formant in formants:
            df[formant] *= 100.
        return df

@DocString
@Columns(
    required=['speaker', 'vowel']
)
@Keywords(
    required=['schwa']
)
class SchwaNormalizer(WattFabriciusNormalizer):
    r"""
    .. math::

        F_i^\prime = \frac{F_i}{F_{i[/ə/]}} - 1

    """
    def __init__(self, **kwargs):
        super(SchwaNormalizer, self).__init__(**kwargs)
        self.actions.update(
            speaker=self.speaker_stats
        )
        self.groups = ['speaker']

    @staticmethod
    def speaker_stats(df, **kwargs):  # pylint: disable=C0111
        constants = kwargs['constants']
        formants = kwargs['formants']
        vowel = kwargs.get('vowel', 'vowel')
        schwa = kwargs['schwa']

        for formant in formants:
            constants['{}_centroid'.format(formant)] = (
                df[df[vowel] == schwa][formant].mean())

    def _norm(self, df, **kwargs):
        formants = kwargs['formants']
        df = super(SchwaNormalizer, self)._norm(df, **kwargs)
        for formant in formants:
            df[formant] -= 1
        return df
