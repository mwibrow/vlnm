"""
Standardize normalizers
~~~~~~~~~~~~~~~~~~~~~~~
"""

import numpy as np

from .base import FormantExtrinsicNormalizer


class SpeakerIntrinsicNormalizer(FormantExtrinsicNormalizer):
    """Base class for speaker intrinsic normalizers."""
    required_columns = ['speaker']

    def _partition(self, df, **kwargs):
        column = kwargs.get('speaker', 'speaker')
        df.groupby(column, as_index=False).apply(self._norm)


class LCENormalizer(SpeakerIntrinsicNormalizer):
    r"""

    .. math::

        F_i^\prime = \frac{F_i}{\max{F_i}}

    """

    def _norm(self, df, **kwargs):
        formants = kwargs.get('formants')
        df[formants] = df[formants] / df[formants].max(axis=0)
        return df

class GerstmanNormalizer(SpeakerIntrinsicNormalizer):
    r"""

    .. math::

        F_i^\prime = \frac{F_i - \min{F_i}}{\max{F_i}}

    """

    def _norm(self, df, **kwargs):
        formants = kwargs.get('formants', [])
        fmin = df[formants].max(axis=0)
        fmax = df[formants].max(axis=0)
        df[formants] = 999 * (df[formants] - fmin) / (fmax - fmin)
        return df

class LobanovNormalizer(SpeakerIntrinsicNormalizer):
    r"""

    .. math::

        F_i^\prime = \frac{F_i - \mu_{F_i}}{\sigma_{F_i}}

    Where :math:`\mu_{F_i}` and :math:`\sigma_{F_i}` are the
    mean and standard deviation (respectively) of the
    formant :math:`F_i` for a given speaker.

    """

    def _norm(self, df, **kwargs):
        formants = kwargs.get('formants', [])
        mean = df[formants].mean(axis=1)
        std = df[formants].std(axis=1)
        df[formants] = (df[formants] - mean) / std
        return df

class NearyNormalizer(SpeakerIntrinsicNormalizer):
    r"""

    .. math::

        F_i^\prime = T\left(
            \log\left(F_i\right) - \frac{1}{n-m+1}
                \sum_{j=m}^{n}\mu_{\log\left(F_j\right)}
        \right)

    Where :math:`T(x)=x` or :math:`T(x)=\exp(x)`,
    and :math:`m = n = i` or :math:`m = 0` and :math:`n = 3`

    """
    transform = None

    def _norm(self, df, **kwargs):
        formants = kwargs.get('formants', [])
        df[formants] -= np.log(df[formants].dropba()).mean(axis=0)
        transform = kwargs.get('transform')
        if transform:
            df[formants] = np.exp(df[formants])
        return df

class NearyGMNormalizer(SpeakerIntrinsicNormalizer):
    r"""

    .. math::

        F_i^\prime = T\left(
            \log\left(F_i\right) - \frac{1}{n - m+ 1}
                \sum_{j=m}^{n}\mu_{\log\left(F_j\right)}
        \right)

    Where :math:`T(x)=x` or :math:`T(x)=\exp(x)`,
    and `m` and `n` are the lowest and hights formant indexes, respectively.

    """

    def _norm(self, df, **kwargs):
        formants = kwargs.get('formants', [])
        df[formants] -= np.log(df[formants].dropba()).mean(axis=0).mean()
        transform = kwargs.get('transform')
        if transform:
            df[formants] = np.exp(df[formants])
        return df
