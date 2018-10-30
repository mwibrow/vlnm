"""
Transform normalizers
~~~~~~~~~~~~~~~~~~~~~
"""
import numpy as np

from vlnm.normalizers import Register

from vlnm.normalizers.base import (
    FormantIntrinsicNormalizer)
from vlnm.conversion import (
    hz_to_bark,
    hz_to_erb,
    hz_to_mel)
from vlnm.normalizers.documentation import DocString
from vlnm.normalizers.validation import (
    Columns,
    Keywords)

@Register('bark')
@DocString
@Columns(
    choice=dict(
        formants=['f0', 'f1', 'f2', 'f3']
    )
)
@Keywords(
    optional=['hz_to_bark']
)
class BarkNormalizer(FormantIntrinsicNormalizer):
    r"""
    Normalise vowels using the Bark scale.

    .. math::

        F_i^N =  26.81 \ln\left(
            1 + \frac{F_i}{F_i + 1960}
            \right) - 0.53

    {{columns}}
    {{keywords}}
    """
    def _norm(self, df, **kwargs):
        """
        Transform formants.
        """
        formants = kwargs.get('formants')
        convert = kwargs.get('hz_to_bark', hz_to_bark)
        df[formants] = convert(df[formants])
        return df

@Register('erb')
@DocString
@Columns(
    choice=dict(
        formants=['f0', 'f1', 'f2', 'f3']
    )
)
@Keywords(
    optional=['hz_to_erb']
)
class ErbNormalizer(FormantIntrinsicNormalizer):
    r"""
    Normalise vowels

    .. math::

       F_i^N = 21.4 \ln\left(1 + 0.00437{F_i}\right)

    {{columns}}
    """
    def _norm(self, df, **kwargs):
        """
        Transform formants.
        """
        formants = kwargs.get('formants')
        convert = kwargs.get('hz_to_erb', hz_to_erb)
        df[formants] = convert(df[formants])
        return df


@Register('log10')
@DocString
@Columns(
    choice=dict(
        formants=['f0', 'f1', 'f2', 'f3']
    )
)
@Keywords(
    optional=['aliases', 'rename']
)
class Log10Normalizer(FormantIntrinsicNormalizer):
    r"""
    Normalize using the base 10 logarithm of the formant values.

     .. math::

       F_i^N = \log_{10}\left(F_i\right)

    """
    def _norm(self, df, **kwargs):
        """
        Transform formants.
        """
        formants = kwargs.get('formants')
        df[formants] = np.log10(df[formants])
        return df


@Register('log')
@DocString
@Columns(
    choice=dict(
        formants=['f0', 'f1', 'f2', 'f3']
    )
)
class LogNormalizer(FormantIntrinsicNormalizer):
    r"""
    Normalize using the natural logarithm of the formant values.

     .. math::

       F_i^N = \log\left(F_i\right)

    {{columns}}
    """
    def _norm(self, df, **kwargs):
        """
        Transform formants.
        """
        formants = kwargs.get('formants')
        df[formants] = np.log(df[formants])
        return df


@Register('mel')
@DocString
@Columns(
    choice=dict(
        formants=['f0', 'f1', 'f2', 'f3']
    )
)
@Keywords(
    optional=['hz_to_mel']
)
class MelNormalizer(FormantIntrinsicNormalizer):
    r"""
    Normalise vowels using the Mel scale.

    .. math::

       F_i^N = 1127 \ln\left(1 + \frac{F_i}{700}\right)

    {{columns}}
    """
    def _norm(self, df, **kwargs):
        """
        Transform formants.
        """
        formants = kwargs.get('formants')
        convert = kwargs.get('hz_to_mel', hz_to_mel)
        df[formants] = convert(df[formants])
        return df


@Register('barkdiff')
@DocString
@Columns(
    required=['f0', 'f1', 'f2', 'f3'],
    returns=['z1-z0', 'z2-z1', 'z3-z2']
)
@Keywords(
    optional=['f0', 'hz_to_bark']
)
class BarkDifferenceNormalizer(FormantIntrinsicNormalizer):
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
