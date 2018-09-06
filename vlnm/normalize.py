"""
Vowel normalizer module
"""

import vlnm.decorators as decorators
from vlnm.utils import (
    merge_columns
)
class VowelNormalizer:
    """
    Base class for vowel normalizers.
    """
    _column_spec = {}

    def __init__(self, **kwargs):
        self.default_kwargs = kwargs

    
    def normalize(self, df, **kwargs):
        """Normalize the formant data in a data frame.

        """
        current_kwargs = {}
        current_kwargs.update(self.default_kwargs, kwargs)
