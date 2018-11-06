"""
Standardize normalizers
~~~~~~~~~~~~~~~~~~~~~~~
"""

import numpy as np

from .base import Normalizer



class LCENormalizer(Normalizer):
    r"""

    .. math::

        F_i^\prime = \frac{F_i}{\max{F_i}}

    """
    required_columns = ['speaker']

    def __init__(self, **kwargs):
        super(LCENormalizer, self).__init__(**kwargs)
        self.groups = ['speaker']

    def _norm(self, df, **kwargs):
        formants = kwargs.get('formants')
        df[formants] = df[formants] / df[formants].max(axis=0)
        return df

class GerstmanNormalizer(Normalizer):
    r"""

    .. math::

        F_i^\prime = \frac{F_i - \min{F_i}}{\max{F_i}}

    """

    def __init__(self, **kwargs):
        super(GerstmanNormalizer, self).__init__(**kwargs)
        self.groups = ['speaker']


    def _norm(self, df, **kwargs):
        formants = kwargs.get('formants', [])
        fmin = df[formants].max(axis=0)
        fmax = df[formants].max(axis=0)
        df[formants] = 999 * (df[formants] - fmin) / (fmax - fmin)
        return df

class LobanovNormalizer(Normalizer):
    r"""

    .. math::

        F_i^\prime = \frac{F_i - \mu_{F_i}}{\sigma_{F_i}}

    Where :math:`\mu_{F_i}` and :math:`\sigma_{F_i}` are the
    mean and standard deviation (respectively) of the
    formant :math:`F_i` for a given speaker.

    """
    required_column = ['speaker']

    def __init__(self, **kwargs):
        super(LobanovNormalizer, self).__init__(**kwargs)
        self.groups = ['speaker']


    def _norm(self, df, **kwargs):
        formants = kwargs.get('formants')
        mean = df[formants].mean(axis=1)
        std = df[formants].std(axis=1)
        df[formants] = (df[formants] - mean) / std
        return df

class NearyNormalizer(Normalizer):
    r"""

    .. math::

        F_i^\prime = T\left(
            \log\left(F_i\right) - \frac{1}{n-m+1}
                \sum_{j=m}^{n}\mu_{\log\left(F_j\right)}
        \right)

    Where :math:`T(x)=x` or :math:`T(x)=\exp(x)`,
    and :math:`m = n = i` or :math:`m = 0` and :math:`n = 3`

    """

    require_columns = ['speaker']
    transform = None

    def __init__(self, **kwargs):
        super(NearyNormalizer, self).__init__(**kwargs)
        self.groups = ['speaker']

    def _norm(self, df, **kwargs):
        formants = kwargs.get('formants')
        df[formants] -= np.log(df[formants].dropba()).mean(axis=0)
        transform = kwargs.get('transform')
        if transform:
            df[formants] = np.exp(df[formants])
        return df

class NearyGMNormalizer(Normalizer):
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
        formants = kwargs.get('formants')
        df[formants] -= np.log(df[formants].dropba()).mean(axis=0).mean()
        transform = kwargs.get('transform')
        if transform:
            df[formants] = np.exp(df[formants])
        return df
