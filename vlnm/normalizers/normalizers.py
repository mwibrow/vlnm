"""
Normalizers
"""
import numpy as np

from vlnm.normalizers.base import (
    FORMANTS,
    VowelNormalizer,
    FormantIntrinsicNormalizer)
from vlnm.conversion import (
    hz_to_bark,
    hz_to_erb,
    hz_to_mel)
from vlnm.normalizers.documentation import DocString
from vlnm.normalizers.validation import (
    Columns,
    Keywords)


@DocString
@Columns(
    choice=dict(
        formants=['f0', 'f1', 'f2', 'f3']
    )
)
@Keywords(
    optional=['hz_to_bark']
)
class BarkNormalizer(FormantIntrinsicNormalizer):
    r"""
    Normalise vowels using the Bark scale.

    .. math::

        F_i^N =  26.81 \ln\left(
            1 + \displayfrac{F_i}{\displayfrac{F_i} + 1960}
            \right) - 0.53

    {{columns}}
    """
    def norm(self, df, **kwargs):
        """
        Transform formants.
        """
        formants = kwargs.get('formants')
        convert = kwargs.get('hz_to_bark', hz_to_bark)
        df[formants] = convert(df[formants])
        return df

@DocString
@Columns(
    choice=dict(
        formants=['f0', 'f1', 'f2', 'f3']
    )
)
@Keywords(
    optional=['hz_to_erb']
)
class ErbNormalizer(FormantIntrinsicNormalizer):
    r"""
    Normalise vowels

    .. math::

       F_i^N = 21.4 \ln\left(1 + 0.00437{F_i}\right)

    {{columns}}
    """
    def norm(self, df, **kwargs):
        """
        Transform formants.
        """
        formants = kwargs.get('formants')
        convert = kwargs.get('hz_to_erb', hz_to_erb)
        df[formants] = convert(df[formants])
        return df


@DocString
@Columns(
    choice=dict(
        formants=['f0', 'f1', 'f2', 'f3']
    )
)
@Keywords(
    optional=['aliases', 'rename']
)
class Log10Normalizer(FormantIntrinsicNormalizer):
    r"""
    Normalize using the base 10 logarithm of the formant values.

     .. math::

       F_i^N = \log_{10}\left(F_i\right)

    """
    def norm(self, df, **kwargs):
        """
        Transform formants.
        """
        formants = kwargs.get('formants')
        df[formants] = np.log10(df[formants])
        return df


@DocString
@Columns(
    choice=dict(
        formants=['f0', 'f1', 'f2', 'f3']
    )
)
class LogNormalizer(FormantIntrinsicNormalizer):
    r"""
    Normalize using the natural logarithm of the formant values.

     .. math::

       F_i^N = \log\left(F_i\right)

    {{columns}}
    """
    def norm(self, df, **kwargs):
        """
        Transform formants.
        """
        formants = kwargs.get('formants')
        df[formants] = np.log(df[formants])
        return df



@DocString
@Columns(
    choice=dict(
        formants=['f0', 'f1', 'f2', 'f3']
    )
)
@Keywords(
    optional=['hz_to_mel']
)
class MelNormalizer(FormantIntrinsicNormalizer):
    r"""
    Normalise vowels using the Mel scale.

    .. math::

       F_i^N = 1127 \ln\left(1 + \displayfrac{F_i}{700}\right)

    {{columns}}
    """
    def norm(self, df, **kwargs):
        """
        Transform formants.
        """
        formants = kwargs.get('formants')
        convert = kwargs.get('hz_to_mel', hz_to_mel)
        df[formants] = convert(df[formants])
        return df


def infer_gender_labels(df, gender, female=None, male=None):
    """
    Infer female and male gender labels.
    """
    labels = df[gender].dropna().unique()
    if female and not male:
        male_labels = [label for label in labels if not label == female]
        male = male_labels[0] if male_labels else None
    elif male and not female:
        female_labels = [label for label in labels if not label == male]
        female = female_labels[0] if female_labels else None
    return female, male


@DocString
@Columns(
    required=['gender'],
    choice=dict(
        formants=['f0', 'f1', 'f2', 'f3']
    )
)
@Keywords(
    choice=dict(
        gender_label=['female', 'male']
    )
)
class BladenNormalizer(VowelNormalizer):
    r"""
    .. math::

        F_{ik}^N = 26.81 \ln\left(
            1 + \displayfrac{F_i}{\displayfrac{F_i} + 1960}
            \right) - 0.53 - I(s_k)

    Where :math:`I(s_k)` is an indicator function returning 1 if
    speaker :math:`k` is identified/identifying as female and 0 otherwise.
    """

    def norm(self, df, **kwargs):
        aliases = kwargs.get('aliases')
        gender = kwargs.get('gender') or aliases.get('gender') or 'gender'
        formants = [column for column in df.columns
                    if column in FORMANTS]  # Ugh

        female, _male = infer_gender_labels(
            df,
            gender,
            female=kwargs.get('female'),
            male=kwargs.get('male'))
        indicator = np.repeat(
            np.atleast_2d(
                (df[gender] == female).astype(float)),
            len(formants),
            axis=0).T
        return hz_to_bark(df[formants]) - indicator

@DocString
@Columns(
    required=['f1', 'f3', 'gender']
)
@Keywords(
    choice=dict(
        gender_label=['female', 'male']
    )
)
class NordstromNormalizer(VowelNormalizer):
    r"""
    ..math::

        F_i^\prime F_i \left(
                1 + I(F_i)\left(
                    \displayfrac{
                        \mu_{F_3}^{\mbox{male}}
                    }{
                        \mu_{F_3}^{\mbox{female}}
                    }
                \right)
            \right

    Where :math:`\mu_{F_3}` is the mean :math:`F_3` across
    all vowels where :math:`F_1` is greater than 600Hz,
    and :math:`I(F_i)` is an indicator function which
    returns 1 if :math:`F_i` is from a speaker
    identified/identifying as female, and 0 otherwise.
    """

    def __init__(self, **kwargs):
        super(NordstromNormalizer, self).__init__(**kwargs)
        self.groups = ['gender']
        self.actions.update(
            gender=self.calculate_f3_means)

    @staticmethod
    def calculate_f3_means(df, **kwargs):
        """
        Calculate the f3 means.
        """
        constants = kwargs.get('constants')
        gender = kwargs.get('gender')
        female, male = infer_gender_labels(
            df,
            gender,
            female=kwargs.get('female'),
            male=kwargs.get('male'))
        constants['mu_female'] = df[
            (df[gender] == female) & (df['f1'] > 600)]['f3'].mean()
        constants['mu_male'] = df[
            (df[gender] == male) & (df['f1'] > 600)]['f3'].mean()

    def norm(self, df, **kwargs):
        constants = kwargs['constants']
        gender = kwargs['gender']
        formants = [column for column in df.columns
                    if column in FORMANTS]  # Ugh

        female, _male = infer_gender_labels(
            df,
            gender,
            female=kwargs.get('female'),
            male=kwargs.get('male'))

        indicator = np.repeat(
            np.atleast_2d(
                (df[gender] == female).astype(float)),
            len(formants),
            axis=0).T

        mu_female, mu_male = constants['mu_female'], constants['mu_male']
        df[formants] = (
            df[formants] * (
                1. + indicator * mu_male / mu_female))
        return df



@DocString
@Columns(
    required=['f0', 'f1', 'f2', 'f3'],
    returns=['z1-z0', 'z2-z1', 'z3-z2']
)
@Keywords(
    optional=['f0', 'hz_to_bark']
)
class BarkDifferenceNormalizer(VowelNormalizer):
    r"""
    .. math::

        F_{i}^N = B_i - B^\prime

    Where :math:`B_i` is a function converting the ith
    frequency measured in hertz to the Bark scale, and
    :math:`B^\prime` is :math:`B_0` or :math:`B_1`
    depending on the context.
    """

    def norm(self, df, **kwargs):

        convert = kwargs.get('hz_to_bark', hz_to_bark)

        z0 = convert(df['f0']) if 'f0' in df else None
        z1 = convert(df['f1'])
        z2 = convert(df['f2'])
        z3 = convert(df['f3'])

        if z0 is not None:
            df['z1-z0'] = z1 - z0
        df['z2-z1'] = z2 - z1
        df['z3-z2'] = z3 - z2

        drop = [
            column for column in df.columns
            if column in ['f0', 'f1', 'f2', 'f3', 'f4']]
        df = df.drop(drop, axis=1)

        return df


@DocString
@Columns(
    required=['speaker']
)
class LCENormalizer(VowelNormalizer):
    r"""

    ..math::

        F_i^\prime F_i \displayfrac{F_i}{\max{F_i}}

    """

    def __init__(self, **kwargs):
        super(LCENormalizer, self).__init__(**kwargs)
        self.actions.update(
            speaker=self.get_speaker_max
        )
        self.groups = ['speaker']

    @staticmethod
    def get_speaker_max(df, **kwargs):
        """Maximum formant values for a speaker."""
        constants = kwargs.get('constants')
        formants = kwargs.get('formants', [])
        for formant in formants:
            key = '{}_max'.format(formant)
            constants[key] = df[formant].max()

    def norm(self, df, **kwargs):
        constants = kwargs.get('constants')
        formants = kwargs.get('formants')
        if not constants or not formants:
            return df

        for formant in formants:
            df[formant] = df[formant] / constants.get('{}_max'.format(formant))
        return df

@DocString
@Columns(
    required=['speaker']
)
class GerstmanNormalizer(VowelNormalizer):
    r"""

    ..math::

        F_i^\prime F_i \displayfrac{F_i - \min{F_i}}{\max{F_i}}

    """

    def __init__(self, **kwargs):
        super(GerstmanNormalizer, self).__init__(**kwargs)
        self.actions.update(
            speaker=self.speaker_range
        )
        self.groups = ['speaker']

    @staticmethod
    def speaker_range(df, **kwargs):
        """Maximum and minimum formant values for a speaker."""
        constants = kwargs.get('constants')
        formants = kwargs.get('formants')
        for formant in formants:
            constants['{}_max'.format(formant)] = df[formant].max()
            constants['{}_min'.format(formant)] = df[formant].min()


    def norm(self, df, **kwargs):
        constants = kwargs.get('constants', [])
        formants = kwargs.get('formants', [])

        for formant in formants:
            fmin = constants['{}_min'.format(formant)]
            fmax = constants['{}_max'.format(formant)]
            df[formant] = 999 * (df[formant] - fmin) / (fmax - fmin)
        return df

@DocString
@Columns(
    required=['speaker']
)
class LobanovNormalizer(VowelNormalizer):
    r"""

    ..math::

        F_i^\prime F_i \displayfrac{F_i - \mu_{F_i}}{\sigma{F_i}}

    Where :math:`\mu_{F_i}` and :math:`\sigma{F_i}` are the
    mean and standard deviation (respectively) of the
    formant :math:`F_i` for a given speaker.

    """
    def __init__(self, **kwargs):
        super(LobanovNormalizer, self).__init__(**kwargs)
        self.actions.update(
            speaker=self.speaker_stats
        )
        self.groups = ['speaker']

    @staticmethod
    def speaker_stats(df, **kwargs):
        """Mean and and standard deviation formant values for a speaker."""

        constants = kwargs.get('constants')
        formants = kwargs.get('formants')

        for formant in formants or []:
            constants['{}_mu'.format(formant)] = df[formant].mean()
            constants['{}_sigma'.format(formant)] = df[formant].std() or 0.


    def norm(self, df, **kwargs):
        constants = kwargs.get('constants')
        formants = kwargs.get('formants')

        for formant in formants:
            f_mu = constants['{}_mu'.format(formant)]
            f_sigma = constants['{}_sigma'.format(formant)]
            df[formant] = (df[formant] - f_mu) / f_sigma if f_sigma else 0.
        return df


@DocString
@Columns(
    required=['speaker'],
    optional=['transform']
)
class NearyNormalizer(VowelNormalizer):
    r"""

    ..math::

        F_i^\prime = T\left(
            \log\left(F_i\right) - \frac{1}{n-m+1}
                \sum_{j=m}{n}\mu_{\log\left(F_j\right)}
        \right)

    Where :math:`T(x)=x` or :math:`T(x)=\exp(x)`,
    and :math:`m = n = i` or :math:`m = 0` and :math:`n = 3`

    """

    def __init__(self, **kwargs):
        super(NearyNormalizer, self).__init__(**kwargs)
        self.actions.update(
            speaker=self.speaker_stats
        )
        self.groups = ['speaker']

    @staticmethod
    def speaker_stats(df, **kwargs):
        """Mean log for speaker formants."""
        constants = kwargs.get('constants')
        formants = kwargs.get('formants')
        for formant in formants:
            constants['{}_mu_log'.format(formant)] = (
                np.mean(np.log(df[formant].dropna())))

    def norm(self, df, **kwargs):
        constants = kwargs.get('constants')
        formants = kwargs.get('formants')

        for formant in formants:
            df[formant] = (
                np.log(df[formant].dropna()) -
                constants['{}_mu_log'.format(formant)])
        transform = kwargs.get('transform')
        if transform:
            df[formants] = np.exp(df[formants])
        return df


@DocString
@Columns(
    required=['speaker'],
    optional=['transform']
)
class NearyGMNormalizer(NearyNormalizer):
    r"""

    ..math::

        F_i^\prime = T\left(
            \log\left(F_i\right) - \frac{1}{n - m+ 1}
                \sum_{j=m}{n}\mu_{\log\left(F_j\right)}
        \right)

    Where :math:`T(x)=x` or :math:`T(x)=\exp(x)`,
    and `m` and `n` are the lowest and hights formant indexes, respectively.

    """

    def __init__(self, **kwargs):
        super(NearyGMNormalizer, self).__init__(**kwargs)
        self.actions.update(
            speaker=self.speaker_stats
        )
        self.groups = ['speaker']

    @staticmethod
    def speaker_stats(df, **kwargs):
        """Mean log for speaker formants."""
        constants = kwargs.get('constants')
        formants = kwargs.get('formants')
        mu_log = np.mean(np.mean(np.log(df[formants].dropna())))
        for formant in formants:
            constants['{}_mu_log'.format(formant)] = mu_log


@DocString
@Columns(
    required=['speaker', 'vowel', 'f1', 'f2']
)
@Keywords(
    required=['fleece', 'trap']
)
class WattFabriciusNormalizer(VowelNormalizer):
    r"""
    ..math::

        F_i^\prime = \frac{F_i}{S(F_i)}

    Where:

    ..math::

        S(F_j) = \frac{1}{3}\left(F_j[/i/] + F_j[/a/] + F_j[/u^\prime/]\right)

    and

    ..math::

        F_1[/u^\prime/] = F_2[/u^\prime/] = F_1[/i/]

    """
    def __init__(self, **kwargs):
        super(WattFabriciusNormalizer, self).__init__(**kwargs)
        self.actions.update(
            speaker=self.speaker_stats
        )
        self.groups = ['speaker']

    @staticmethod
    def speaker_stats(df, **kwargs):
        """
        Calculate the speakers centroid.
        """
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

    def norm(self, df, **kwargs):
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
    ..math::

        F_i^\prime = \frac{F_i}{S(F_i)}

    Where:

    ..math::

        S(F_j) = \begin{cases}
            \frac{1}{2}\left(F_j[/i/] + F_j[/u^\prime/]\right)
            & \text{when } j = 2
            \\
            \frac{1}{3}\left(F_j[/i/] + F_j[/a/] + F_j[/u^\prime/]\right)
            & text{otherwise}
        \end{cases}

    and

    ..math::

        F_1[/u^\prime/] = F_2[/u^\prime/] = F_1[/i/]

    """

    @staticmethod
    def speaker_stats(df, **kwargs):
        """
        Calculate the speakers centroid.
        """
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
    ..math::

        F_i^\prime = \frac{F_i}{S(F_i)}

    Where:

    ..math::

        S(F_j) = \begin{cases}
            \frac{1}{2}\left(F_j[/i/] + F_j[/u^\prime/]\right)
            & \text{when } j = 2
            \\
            \frac{1}{3}\left(F_j[/i/] + F_j[/a/] + F_j[/u^\prime/]\right)
            & text{otherwise}
        \end{cases}

    and

    ..math::

        F_j[/u^\prime/] = \text{argmin}_\rho \mu_{F_k[rho \in P]}

    where :math:`P` is the set of point vowels.
    """

    @staticmethod
    def speaker_stats(df, **kwargs):
        """
        Calculate the speakers centroid.
        """
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
    ..math::

        F_i^\prime = \frac{F_i}{S(F_i)}

    Where:

    ..math::

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
    def speaker_stats(df, **kwargs):
        """
        Calculate the speakers centroid.
        """
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

    def norm(self, df, **kwargs):
        formants = kwargs['formants']
        df = super(BighamNormalizer, self).norm(df, **kwargs)
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
    ..math::

        F_i^\prime = \frac{F_i}{F_i[/ə/]} - 1

    """
    def __init__(self, **kwargs):
        super(SchwaNormalizer, self).__init__(**kwargs)
        self.actions.update(
            speaker=self.speaker_stats
        )
        self.groups = ['speaker']

    @staticmethod
    def speaker_stats(df, **kwargs):
        """
        Calculate the speakers centroid.
        """
        constants = kwargs['constants']
        formants = kwargs['formants']
        vowel = kwargs.get('vowel', 'vowel')
        schwa = kwargs['schwa']

        for formant in formants:
            constants['{}_centroid'.format(formant)] = (
                df[df[vowel] == schwa][formant].mean())

    def norm(self, df, **kwargs):
        formants = kwargs['formants']
        df = super(SchwaNormalizer, self).norm(df, **kwargs)
        for formant in formants:
            df[formant] -= 1
        return df
