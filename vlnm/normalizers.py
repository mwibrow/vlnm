"""
Normalizers
"""
import numpy as np

from vlnm.decorators import (
    docstring as DocString,
    columns as Columns
)

from vlnm.normalize import (
    VowelNormalizer,
    FormantIntrinsicNormalizer
)

@DocString
@Columns(
    formants=['f0', 'f1', 'f2', 'f3']
)
class Log10Normalizer(FormantIntrinsicNormalizer):
    r"""
    Normalize using the base 10 logarithm of the formant values.

     .. math::

       F_i^N = \log_{10}\left(F_i\right)

    {% columns %}
    """
    def _transform(self, df):
        """
        Normalize using log10
        """
        return np.log10(df)
