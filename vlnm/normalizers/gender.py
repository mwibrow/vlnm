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
    config = dict(
        columns=['gender'],
        keywords=['gender', 'male', 'female']
    )

    def _keyword_default(self, keyword, df=None):
        if keyword == 'female':
            return 'F'
        elif keyword == 'male':
            return 'M'
        return super()._keyword_default(keyword, df=df)

    def _norm(self, df):
        gender = self.params['gender']
        formants = self.params['formants']
        female = self.params['female']
        indicator = np.repeat(
            np.atleast_2d(
                (df[gender] == female).astype(float)),
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
    config = dict(
        columns=['f1', 'f3', 'gender'],
        keywords=['male', 'female'],
        groups=['gender']
    )

    def _keyword_default(self, keyword, df=None):
        if keyword == 'female':
            return 'F'
        elif keyword == 'male':
            return 'M'
        return super()._keyword_default(keyword, df=df)

    def _prenormalize(self, df):
        return self.get_f3_means(df)

    def get_f3_means(self, df):
        """Calculate the mean F3 for all speakers."""
        gender = self.options['gender']
        female = self.options['female']

        constants = {}
        constants['mu_female'] = df[
            (df[gender] == female) & (df['f1'] > 600)]['f3'].mean()
        constants['mu_male'] = df[
            (df[gender] != female) & (df['f1'] > 600)]['f3'].mean()
        self.options['constants'] = constants
        return df


    def _norm(self, df):
        constants = self.params['constants']
        gender = self.params['gender']
        formants = self.params['formants']

        female = self.params['female']

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
