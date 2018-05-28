"""
Normalization methods.
"""
# pylint: disable=no-self-use

import numpy as np

from vlnm.conversion import (
    hz_to_bark,
    hz_to_mel,
    hz_to_erb)

from vlnm.normalize import VowelNormalizer


class FormantIntrinsicNormalizer(VowelNormalizer):
    r"""
    Base class for formant-intrinsic normaliztion.
    """

    required = ['formants']

    def _normalize_df(self, df, cols_in, cols_out, **__):
        df[cols_in] = df[cols_out]
        return df

    def normalize(self, df, **kwargs):
        """
        Normalize the a data frame.

        Paramters
        ---------
        df: pandas.DataFrame
        """
        return self._normalize(
            df,
            margins=[],
            callbacks=[self._normalize_df],
            **kwargs)


class Log10Normalizer(FormantIntrinsicNormalizer):
    r"""
    Normalize using the base 10 logarithm of the formant values.

     .. math::

       F_i^N = \log_{10}\left(F_i\right)
    """
    def _normalize_df(self, df, cols_in, cols_out, **__):
        """
        Normalize using log10
        """
        df[cols_out] = np.log10(df[cols_in])
        return df


class LogNormalizer(FormantIntrinsicNormalizer):
    r"""
    Normalize using the natural logarithm of the formant values.

     .. math::

       F_i^N = \log\left(F_i\right)
    """
    def _normalize_df(self, df, cols_in, cols_out, **__):
        df[cols_out] = np.log(df[cols_in])
        return df


class MelNormalizer(FormantIntrinsicNormalizer):
    r"""
    Normalise vowels using the Mel scale.

    .. math::

       F_i^N = 1127 \ln\left(1 + \displayfrac{F_i}{700}\right)

    """
    def _normalize_df(self, df, cols_in, cols_out, **__):
        df[cols_out] = hz_to_mel(df[cols_in])
        return df


class BarkNormalizer(FormantIntrinsicNormalizer):
    r"""
    Normalise vowels using the Bark scale.

    .. math::

        F_i^N =  26.81 \ln\left(
            1 + \displayfrac{F_i}{\displayfrac{F_i} + 1960}
            \right) - 0.53
    """
    def _normalize_df(self, df, cols_in, cols_out, **__):
        df[cols_out] = hz_to_bark(df[cols_in])
        return df


class ErbNormalizer(FormantIntrinsicNormalizer):
    r"""
    Normalise vowels

    .. math::

       F_i^N = 21.4 \ln\left(1 + 0.00437{F_i}\right)

    """
    def _normalize_df(self, df, cols_in, cols_out, **__):
        df[cols_out] = hz_to_erb(df[cols_in])
        return df


class BladenNormalizer(VowelNormalizer):
    r"""
    .. math::

        F_{ik}^N = 26.81 \ln\left(
            1 + \displayfrac{F_i}{\displayfrac{F_i} + 1960}
            \right) - 0.53 - I(s_k)

    Where :math:`I(s_k)` is an indicator function returning 1 if speaker :math:`k`
    is identified/identifying as female and 0 otherwise.
    """
    required = ['formants', 'gender']
    one_from = [['male', 'female']]

    def _normalize_df(self, df, cols_in, cols_out, **kwargs):
        gender = kwargs['gender']
        female, _male = infer_gender_labels(
            df,
            gender,
            female=kwargs.get('female'),
            male=kwargs.get('male'))
        indicator = np.repeat(
            np.atleast_2d(
                (df[gender] == female).astype(float)),
            len(cols_in),
            axis=0).T
        df[cols_out] = hz_to_bark(df[cols_in]) - indicator
        return df

    def normalize(self, df, **kwargs):
        """
        Normalize the a data frame.

        Paramters
        ---------
        df: pandas.DataFrame
        """
        margins = kwargs.pop('margins', [])
        callbacks = [None] * (len(margins) - 1) + [self._normalize_df]
        return self._normalize(
            df,
            margins=margins,
            callbacks=callbacks,
            remove_none=True,
            **kwargs)


class BarkDifferenceNormalizer(VowelNormalizer):
    r"""
    .. math::

        F_{i}^N = B_i - B^\prime

    Where :math:`B_i` is a function converting the ith
    frequency measured in hertz to the Bark scale, and
    :math:`B^\prime` is :math:`B_0` or :math:`B_1`
    depending on the context.
    """
    required = ['formants']
    one_from = [['f0', 'f1']]

    def _normalize_df(self, df, cols_in, cols_out, **kwargs):
        f0, f1 = kwargs.get('f0'), kwargs.get('f1')
        offset = np.repeat(
            np.atleast_2d(hz_to_bark(df[f0] if f0 else df[f1])),
            len(cols_in),
            axis=0).T

        df[cols_out] = hz_to_bark(df[cols_in]) - offset
        return df

    def normalize(self, df, **kwargs):
        """
        Normalize the a data frame.

        Paramters
        ---------
        df: pandas.DataFrame
        """
        margins = kwargs.pop('margins', [])
        callbacks = [None] * (len(margins) - 1) + [self._normalize_df]
        return self._normalize(
            df,
            margins=margins,
            callbacks=callbacks,
            remove_none=True,
            **kwargs)


class NordstromNormalizer(VowelNormalizer):
    r"""
    ..math::

        F_i = F_i \left(
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
    required = ['f1', 'f3', 'formants', 'gender']
    one_from = [['male', 'female']]

    def calculate_f3_means(self, df, f1=None, f3=None, constants=None, **kwargs):
        """
        Calculate the f3 means.
        """
        gender = kwargs['gender']
        female, male = infer_gender_labels(
            df,
            gender,
            female=kwargs.get('female'),
            male=kwargs.get('male'))
        constants['mu_female'] = df[(df[gender] == female) & (df[f1] > 600)][f3].mean()
        constants['mu_male'] = df[(df[gender] == male) & (df[f1] > 600)][f3].mean()
        return df

    def _normalize_df(self, df, cols_in, cols_out, constants=None, **kwargs):
        gender = kwargs['gender']
        female, _male = infer_gender_labels(
            df,
            gender,
            female=kwargs.get('female'),
            male=kwargs.get('male'))

        indicator = np.repeat(
            np.atleast_2d(
                (df[gender] == female).astype(float)),
            len(cols_in),
            axis=0).T

        mu_female, mu_male = constants['mu_female'], constants['mu_male']
        df[cols_out] = (
            df[cols_in] * (
                1. + indicator * mu_male / mu_female))
        return df

    def normalize(self, df, **kwargs):
        """
        Normalize the a data frame.

        Paramters
        ---------
        df: pandas.DataFrame
        """
        margins = kwargs.pop('margins', [])
        callbacks = [None] * (len(margins) - 1) + [self.calculate_f3_means,
                                                   self._normalize_df]
        return self._normalize(
            df,
            margins=margins,
            callbacks=callbacks,
            remove_none=True,
            **kwargs)


def infer_gender_labels(df, gender, female=None, male=None):
    """
    Infer female and male gender labels.
    """
    if female and not male:
        male = [label for label in df[gender].unique()
                if not label == female][0]
    elif male and not female:
        female = [label for label in df[gender].unique()
                  if not label == male][0]
    return female, male
