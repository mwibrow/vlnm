"""
Normalizers
"""
import numpy as np

from vlnm.conversion import (
    hz_to_bark,
    hz_to_erb,
    hz_to_mel)
from vlnm.decorators import (
    docstring as DocString,
    columns as Columns)
from vlnm.normalize import (
    VowelNormalizer,
    FormantIntrinsicNormalizer)

@DocString
@Columns(
    formants=['f0', 'f1', 'f2', 'f3']
)
class Log10Normalizer(FormantIntrinsicNormalizer):
    r"""
    Normalize using the base 10 logarithm of the formant values.

     .. math::

       F_i^N = \log_{10}\left(F_i\right)

    {{columns}}
    """
    def transform(self, df, **__):
        """
        Transform formants.
        """
        return np.log10(df)


@DocString
@Columns(
    formants=['f0', 'f1', 'f2', 'f3']
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
    formants=['f0', 'f1', 'f2', 'f3']
)
class MelNormalizer(FormantIntrinsicNormalizer):
    r"""
    Normalise vowels using the Mel scale.

    .. math::

       F_i^N = 1127 \ln\left(1 + \displayfrac{F_i}{700}\right)

    {{columns}}
    """
    def transform(self, df, **_):
        """
        Transform formants.
        """
        return hz_to_mel(df)

@DocString
@Columns(
    formants=['f0', 'f1', 'f2', 'f3']
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
    def transform(self, df, **_):
        """
        Transform formants.
        """
        return hz_to_bark(df)

@DocString
@Columns(
    formants=['f0', 'f1', 'f2', 'f3']
)
class ErbNormalizer(FormantIntrinsicNormalizer):
    r"""
    Normalise vowels

    .. math::

       F_i^N = 21.4 \ln\left(1 + 0.00437{F_i}\right)

    {{columns}}
    """
    def transform(self, df, **_):
        """
        Transform formants.
        """
        return hz_to_erb(df)


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
    formants=['f0', 'f1', 'f2', 'f3'],
    gender_label=['female', 'male']
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
