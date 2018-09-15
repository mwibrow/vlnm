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
    def transform(self, df, **__):
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
    def transform(self, df, **_):
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
    def transform(self, df, **kwargs):
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
    def transform(self, df, **kwargs):
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
    def transform(self, df, **kwargs):
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

    Where :math:`I(s_k)` is an indicator function returning 1 if speaker :math:`k`
    is identified/identifying as female and 0 otherwise.
    """

    def norm(self, df, **kwargs):
        gender = kwargs.get('gender')
        formants = kwargs.get('formants')

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

        columns = [kwargs.get(formant, formant) for formant in formants]
        return hz_to_bark(df[columns]) - indicator


@DocString
@Columns(
    required=['f1', 'f2', 'f3'],
    optional=['f0'],
    returns=['z1-z0', 'z2-z1', 'z3-z2']
)
@Keywords(
    optional=['hz_to_bark']
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
        f0 = kwargs.get('f0')
        f1 = kwargs.get('f1')
        f2 = kwargs.get('f2')
        f3 = kwargs.get('f3')

        z0 = convert(df[f0]) if f0 else None
        z1 = convert(df[f1])
        z2 = convert(df[f2])
        z3 = convert(df[f3])

        if z0:
            df['z1-z0'] = z1 - z0
        df['z2-z1'] = z2 - z1
        df['z3-z2'] = z3 - z2

        return df
