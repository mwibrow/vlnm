"""
Vowel intrinsic normalizers
~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from .base import VowelIntrinsicNormalizer
from ..conversion import hz_to_bark
from ..decorators import (
    Columns,
    DocString,
    Keywords,
    Register)

@Register('barkdiff')
@DocString
@Columns(
    required=['f0', 'f1', 'f2', 'f3'],
    returns=['z1-z0', 'z2-z1', 'z3-z2']
)
@Keywords(
    optional=['f0', 'hz_to_bark']
)
class BarkDifferenceNormalizer(VowelIntrinsicNormalizer):
    r"""
    .. math::

        F_{i}^N = B_i - B^\prime

    Where :math:`B_i` is a function converting the ith
    frequency measured in hertz to the Bark scale, and
    :math:`B^\prime` is :math:`B_0` or :math:`B_1`
    depending on the context.
    """

    def _norm(self, df, **kwargs):

        convert = kwargs.get('hz_to_bark', hz_to_bark)

        z0 = convert(df['f0']) if 'f0' in df else None
        z1 = convert(df['f1'])
        z2 = convert(df['f2'])
        z3 = convert(df['f3'])

        if z0 is not None:
            df['z1-z0'] = z1 - z0
        df['z2-z1'] = z2 - z1
        df['z3-z2'] = z3 - z2

        drop = [
            column for column in df.columns
            if column in ['f0', 'f1', 'f2', 'f3', 'f4']]
        df = df.drop(drop, axis=1)

        return df
