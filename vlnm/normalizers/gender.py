"""
Gender-based normalizers
~~~~~~~~~~~~~~~~~~~~~~~~

Normalizers which adjust calculations based
on the gender identified by the speaker.
"""

import numpy as np

from vlnm.normalizers.base import (
    FORMANTS,
    VowelNormalizer)
from vlnm.conversion import hz_to_bark
from vlnm.decorators import (
    Columns,
    DocString,
    Keywords,
    Register)


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


@Register('bladen')
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
            1 + \frac{F_i}{F_i + 1960}
            \right) - 0.53 - I(s_k)

    Where :math:`I(s_k)` is an indicator function returning 1 if
    speaker :math:`k` is identified/identifying as female and 0 otherwise.
    """

    def _norm(self, df, **kwargs):
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

@Register('nordstrom')
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
    .. math::

        F_i^\prime = F_i \left(
                1 + I(F_i)\left(
                    \frac{
                        \mu_{F_3}^{\small{male}}
                    }{
                        \mu_{F_3}^{\small{female}}
                    }
                \right)
            \right)

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
    def calculate_f3_means(df, **kwargs):  # pylint: disable=C0111
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

    def _norm(self, df, **kwargs):
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
