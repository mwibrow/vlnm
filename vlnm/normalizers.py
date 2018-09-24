"""
Normalizers
"""
import numpy as np

from vlnm.base import (
    FORMANTS,
    VowelNormalizer,
    FormantIntrinsicNormalizer)
from vlnm.conversion import (
    hz_to_bark,
    hz_to_erb,
    hz_to_mel)
from vlnm.documentation import DocString
from vlnm.validation import (
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

    def calculate_f3_means(
            self,
            df,
            **kwargs):  # pylint: disable=no-self-use
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

    def norm(self, df, **kwargs):  # pylint: disable=no-self-use
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

    def get_speaker_max(
            self,
            df,
            formants=None,
            constants=None,
            **__):  # pylint: disable=no-self-use
        """Maximum formant values for a speaker."""
        for formant in formants:
            key = '{}_max'.format(formant)
            constants[key] = df[formant].max()


    def norm(self, df, **kwargs):  # pylint: disable=no-self-use
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

    def speaker_range(
            self,
            df,
            formants=None,
            constants=None,
            **__):  # pylint: disable=no-self-use
        """Maximum and minimum formant values for a speaker."""
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

    def speaker_stats(
            self,
            df,
            **kwargs):  # pylint: disable=no-self-use
        """Mean and and standard deviation formant values for a speaker."""

        constants = kwargs.get('constants')
        formants = kwargs.get('formants')

        for formant in formants or []:
            constants['{}_mu'.format(formant)] = df[formant].mean()
            constants['{}_sigma'.format(formant)] = df[formant].std() or 0.


    def norm(self, df, **kwargs):  # pylint: disable=no-self-use
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
    optional=['method', 'transform']
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

    def speaker_stats(
            self,
            df,
            **kwargs):  # pylint: disable=no-self-use
        """Mean log for speaker formants."""
        constants = kwargs.get('constants')
        formants = kwargs.get('formants')
        method = kwargs.get('method', 'intrinsic')
        if 'extrinsic' in method.lower():
            mu_log = np.mean(np.mean(np.log(df[formants].dropna())))
            for formant in formants:
                constants['{}_mu_log'.format(formant)] = mu_log
        else:
            for formant in formants:
                constants['{}_mu_log'.format(formant)] = (
                    np.mean(np.log(df[formant].dropna())))
        return df

    def norm(self, df, **kwargs):  # pylint: disable=no-self-use
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


class Neary1Normalizer(NearyNormalizer):
    r"""

    ..math::

        F_i^\prime = \log\left(F_i\right) - \mu_{\log\left(F_i\right)}

    Where :math:`\mu_{x}` is the mean of :math:`x`

    """

    def __init__(self, **kwargs):
        kwargs['method'] = 'intrinsic'
        kwargs['transform'] = False
        super(Neary1Normalizer, self).__init__(**kwargs)


class Neary2Normalizer(NearyNormalizer):
    r"""

    ..math::

        F_i^\prime = \log\left(F_i\right) - \frac{1}{N}
            \sum_{j=0}{N}\mu_{\log\left(F_j\right)}

    Where :math:`\mu_{x}` is the mean of :math:`x`

    """

    def __init__(self, **kwargs):
        kwargs['method'] = 'extrinsic'
        kwargs['transform'] = False
        super(Neary2Normalizer, self).__init__(**kwargs)


class Neary1ExpNormalizer(NearyNormalizer):
    r"""

    ..math::

        F_i^\prime = \exp\left(
            \log\left(F_i\right) - \mu_{\log\left(F_i\right)}
        \right)

    Where :math:`\mu_{x}` is the mean of :math:`x`

    """

    def __init__(self, **kwargs):
        kwargs['method'] = 'intrinsic'
        kwargs['transform'] = True
        super(Neary1ExpNormalizer, self).__init__(**kwargs)


class Neary2ExpNormalizer(NearyNormalizer):
    r"""

    ..math::

        F_i^\prime = \exp\left(
            \log\left(F_i\right) - \frac{1}{N}
            \sum_{j=0}{N}\mu_{\log\left(F_j\right)}
        \right)

    Where :math:`\mu_{x}` is the mean of :math:`x`

    """

    def __init__(self, **kwargs):
        kwargs['method'] = 'extrinsic'
        kwargs['transform'] = True
        super(Neary2ExpNormalizer, self).__init__(**kwargs)


@DocString
@Columns(
    required=['speaker', 'vowel']
)
@Keywords(
    required=['fleece', 'trap']
)
class WattFabricius(VowelNormalizer):
    """
    ..math::

        F_i^\prime = \frac{F_i}{S(F_i)}

    Where:

    ..math::

        S(F_j) = F_j[/i/] + F_j[/a/] + F_j[/u^\prime/]

    and

    ..math::

        F_1[/u^\prime/] = F_1[/u^\prime/] = F_1[/i/]

    """
