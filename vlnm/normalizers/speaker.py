"""
Standardize normalizers
~~~~~~~~~~~~~~~~~~~~~~~
"""

import numpy as np

from .base import Normalizer, VowelNormalizer
from ..decorators import (
    Columns,
    DocString,
    Register)


class LCENormalizer(Normalizer):
    r"""

    .. math::

        F_i^\prime = \frac{F_i}{\max{F_i}}

    """
    required_columns = ['speaker']

    def __init__(self, **kwargs):
        super(LCENormalizer, self).__init__(**kwargs)
        self.actions.update(
            speaker=self._get_speaker_max
        )
        self.groups = ['speaker']

    @staticmethod
    def _get_speaker_max(df, **kwargs):
        constants = kwargs.get('constants')
        formants = kwargs.get('formants', [])
        for formant in formants:
            key = '{}_max'.format(formant)
            constants[key] = df[formant].max()

    def _norm(self, df, **kwargs):
        constants = kwargs.get('constants')
        formants = kwargs.get('formants')
        if not constants or not formants:
            return df
        for formant in formants:
            df[formant] = df[formant] / constants.get('{}_max'.format(formant))
        return df

@Register('gerstman')
@DocString
@Columns(
    required=['speaker']
)
class GerstmanNormalizer(VowelNormalizer):
    r"""

    .. math::

        F_i^\prime = \frac{F_i - \min{F_i}}{\max{F_i}}

    """

    def __init__(self, **kwargs):
        super(GerstmanNormalizer, self).__init__(**kwargs)
        self.actions.update(
            speaker=self._speaker_range
        )
        self.groups = ['speaker']

    @staticmethod
    def _speaker_range(df, **kwargs):
        constants = kwargs.get('constants')
        formants = kwargs.get('formants')
        for formant in formants:
            constants['{}_max'.format(formant)] = df[formant].max()
            constants['{}_min'.format(formant)] = df[formant].min()


    def _norm(self, df, **kwargs):
        constants = kwargs.get('constants', [])
        formants = kwargs.get('formants', [])

        for formant in formants:
            fmin = constants['{}_min'.format(formant)]
            fmax = constants['{}_max'.format(formant)]
            df[formant] = 999 * (df[formant] - fmin) / (fmax - fmin)
        return df

@Register('lobanov')
@DocString
@Columns(
    required=['speaker']
)
class LobanovNormalizer(VowelNormalizer):
    r"""

    .. math::

        F_i^\prime = \frac{F_i - \mu_{F_i}}{\sigma_{F_i}}

    Where :math:`\mu_{F_i}` and :math:`\sigma_{F_i}` are the
    mean and standard deviation (respectively) of the
    formant :math:`F_i` for a given speaker.

    """
    def __init__(self, **kwargs):
        super(LobanovNormalizer, self).__init__(**kwargs)
        self.actions.update(
            speaker=self._speaker_stats
        )
        self.groups = ['speaker']

    @staticmethod
    def _speaker_stats(df, **kwargs):
        constants = kwargs.get('constants')
        formants = kwargs.get('formants')

        for formant in formants or []:
            constants['{}_mu'.format(formant)] = df[formant].mean()
            constants['{}_sigma'.format(formant)] = df[formant].std() or 0.


    def _norm(self, df, **kwargs):
        constants = kwargs.get('constants')
        formants = kwargs.get('formants')

        for formant in formants:
            f_mu = constants['{}_mu'.format(formant)]
            f_sigma = constants['{}_sigma'.format(formant)]
            df[formant] = (df[formant] - f_mu) / f_sigma if f_sigma else 0.
        return df

@Register('Neary')
@DocString
@Columns(
    required=['speaker'],
    optional=['transform']
)
class NearyNormalizer(VowelNormalizer):
    r"""

    .. math::

        F_i^\prime = T\left(
            \log\left(F_i\right) - \frac{1}{n-m+1}
                \sum_{j=m}^{n}\mu_{\log\left(F_j\right)}
        \right)

    Where :math:`T(x)=x` or :math:`T(x)=\exp(x)`,
    and :math:`m = n = i` or :math:`m = 0` and :math:`n = 3`

    """

    def __init__(self, **kwargs):
        super(NearyNormalizer, self).__init__(**kwargs)
        self.actions.update(
            speaker=self._speaker_stats
        )
        self.groups = ['speaker']

    @staticmethod
    def _speaker_stats(df, **kwargs):
        constants = kwargs.get('constants')
        formants = kwargs.get('formants')
        for formant in formants:
            constants['{}_mu_log'.format(formant)] = (
                np.mean(np.log(df[formant].dropna())))

    def _norm(self, df, **kwargs):
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

@Register('NearyGM')
@DocString
@Columns(
    required=['speaker'],
    optional=['transform']
)
class NearyGMNormalizer(NearyNormalizer):
    r"""

    .. math::

        F_i^\prime = T\left(
            \log\left(F_i\right) - \frac{1}{n - m+ 1}
                \sum_{j=m}^{n}\mu_{\log\left(F_j\right)}
        \right)

    Where :math:`T(x)=x` or :math:`T(x)=\exp(x)`,
    and `m` and `n` are the lowest and hights formant indexes, respectively.

    """

    def __init__(self, **kwargs):
        super(NearyGMNormalizer, self).__init__(**kwargs)
        self.actions.update(
            speaker=self._speaker_stats
        )
        self.groups = ['speaker']

    @staticmethod
    def _speaker_stats(df, **kwargs):
        constants = kwargs.get('constants')
        formants = kwargs.get('formants')
        mu_log = np.mean(np.mean(np.log(df[formants].dropna())))
        for formant in formants:
            constants['{}_mu_log'.format(formant)] = mu_log
