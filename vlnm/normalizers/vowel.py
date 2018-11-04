"""
Vowel intrinsic normalizers
~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from .base import FormantExtrinsicNormalizer
from ..conversion import hz_to_bark


class BarkDifferenceNormalizer(FormantExtrinsicNormalizer):
    r"""
    .. math::

        F_{i}^N = B_i - B^\prime

    Where :math:`B_i` is a function converting the ith
    frequency measured in hertz to the Bark scale, and
    :math:`B^\prime` is :math:`B_0` or :math:`B_1`
    depending on the context.
    """
    required_keywords = ['f1', 'f2', 'f3']
    transform = hz_to_bark

    def __init__(self, transform=None, **kwargs):
        super(BarkDifferenceNormalizer, self).__init__(
            transform=transform or self.__class__.transform,
            **kwargs)

    def _norm(self, df, **kwargs):

        transform = kwargs.get('transform')
        f0 = kwargs.get('f0')
        f1 = kwargs.get('f1')
        f2 = kwargs.get('f2')
        f3 = kwargs.get('f3')

        z0 = transform(df[f0]) if f0 in df else None
        z1 = transform(df[f1])
        z2 = transform(df[f2])
        z3 = transform(df[f3])

        if z0 is not None:
            df['z1-z0'] = z1 - z0
        df['z2-z1'] = z2 - z1
        df['z3-z2'] = z3 - z2

        return df
