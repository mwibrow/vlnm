"""
Gender-based normalizers
~~~~~~~~~~~~~~~~~~~~~~~~

Normalizers which adjust calculations based
on the gender identified by the speaker.
"""

import numpy as np

from vlnm.normalizers.base import (
    FormantExtrinsicNormalizer,
    FormantIntrinsicNormalizer)
from vlnm.conversion import hz_to_bark


class BladenNormalizer(FormantIntrinsicNormalizer):
    r"""
    .. math::

        F_{ik}^N = 26.81 \left(
            1 + \frac{F_i}{F_i + 1960}
            \right) - 0.53 - I(s_k)

    Where :math:`I(s_k)` is an indicator function returning 1 if
    speaker :math:`k` is identified/identifying as female and 0 otherwise.
    """
    required_columns = ['gender']
    optional_keywords = ['male', 'female']

    def _norm(self, df, **kwargs):
        gender = kwargs.get('gender') or 'gender'
        formants = kwargs.get('formants')

        female = kwargs.get('female', 'F')
        male = kwargs.get('male', 'M')

        is_female = lambda x: x == female if female else lambda x: x != male

        indicator = np.repeat(
            np.atleast_2d(
                (is_female(df[gender])).astype(float)),
            len(formants),
            axis=0).T

        return hz_to_bark(df[formants]) - indicator


class NordstromNormalizer(FormantExtrinsicNormalizer):
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
    required_columns = ['f1', 'f3', 'gender']
    optional_keywords = ['male', 'female']

    def __init__(self, **kwargs):
        super(NordstromNormalizer, self).__init__(**kwargs)
        self.groups = ['gender']

    @staticmethod
    def _prenormalize(df, **kwargs):
        return NordstromNormalizer.get_f3_means(df, **kwargs)

    @staticmethod
    def get_f3_means(df, **kwargs):
        """Calculate the mean F3 for all speakers."""
        constants = kwargs.get('constants')
        gender = kwargs.get('gender')
        female = kwargs.get('female', 'F')
        male = kwargs.get('male', 'M')

        is_female = lambda x: x == female if female else lambda x: x != male

        constants['mu_female'] = df[
            is_female(df[gender]) & (df['f1'] > 600)]['f3'].mean()
        constants['mu_male'] = df[
            ~is_female(df[gender]) & (df['f1'] > 600)]['f3'].mean()
        return df

    @staticmethod
    def _norm(df, **kwargs):
        constants = kwargs['constants']
        gender = kwargs['gender']
        formants = formants = kwargs.get('formants')

        female = kwargs.get('female', 'F')
        male = kwargs.get('male', 'M')

        is_female = lambda x: x == female if female else lambda x: x != male

        indicator = np.repeat(
            np.atleast_2d(
                (is_female(df[gender])).astype(float)),
            len(formants),
            axis=0).T

        mu_female, mu_male = constants['mu_female'], constants['mu_male']
        df[formants] = (
            df[formants] * (
                1. + indicator * mu_male / mu_female))
        return df
