"""
Vowel intrinsic normalizers
~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from . import register_class
from .base import FormantExtrinsicNormalizer
from ..conversion import hz_to_bark

@register_class('barkdiff')
class BarkDifferenceNormalizer(FormantExtrinsicNormalizer):
    r"""
    .. math::

        F_{i}^N = B_i - B^\prime

    Where :math:`B_i` is a function converting the ith
    frequency measured in hertz to the Bark scale, and
    :math:`B^\prime` is :math:`B_0` or :math:`B_1`
    depending on the context.
    """
    config = dict(
        keywords=['f1', 'f2', 'f3'],
        transform=hz_to_bark
    )

    def _norm(self, df):

        transform = self.config['transform']
        f0 = self.params['f0']
        f1 = self.params['f1']
        f2 = self.params['f2']
        f3 = self.params['f3']

        z0 = transform(df[f0]) if f0 in df else None
        z1 = transform(df[f1])
        z2 = transform(df[f2])
        z3 = transform(df[f3])

        if z0 is not None:
            df['z1-z0'] = z1 - z0
        df['z2-z1'] = z2 - z1
        df['z3-z2'] = z3 - z2

        return df
