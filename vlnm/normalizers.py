"""
Normalizers
"""
import numpy as np

from vlnm.conversion import (
    hz_to_bark,
    hz_to_erb,
    hz_to_mel)
from vlnm.documentation import DocString
from vlnm.validation import (
    Columns,
    Keywords)
from vlnm.base import (
    FORMANTS,
    VowelNormalizer,
    FormantIntrinsicNormalizer)

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
    def norm(self, df, **__):
        """
        Transform formants.
        """
        return np.log10(df)


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
    def norm(self, df, **_):
        """
        Transform formants.
        """
        return np.log(df)



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
        convert = kwargs.get('hz_to_mel', hz_to_mel)
        return convert(df)

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
        convert = kwargs.get('hz_to_bark', hz_to_bark)
        return convert(df)

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
        convert = kwargs.get('hz_to_erb', hz_to_erb)
        return convert(df)


def infer_gender_labels(df, gender, female=None, male=None):
    """
    Infer female and male gender labels.
    """
    labels = df[gender].dropna().unique()
    if len(labels) != 2:
        raise ValueError(
            'More than two labels for gender. '
            'Gender-based normalization assumes binary labelling')
    if female and not male:
        male = [label for label in labels
                if not label == female][0]
    elif male and not female:
        female = [label for label in labels
                  if not label == male][0]
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
