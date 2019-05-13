"""
Tests for the formant intrinsic normalizers.
"""

import numpy as np

from vlnm.conversion import (
    hz_to_bark,
    hz_to_erb,
    hz_to_mel)
from vlnm.normalizers.formant import (
    BarkNormalizer,
    ErbNormalizer,
    LogNormalizer,
    Log10Normalizer,
    MelNormalizer)

from tests.helpers import (
    generate_data_frame,
    Helper)


def get_test_dataframe(speakers=8):
    """Generate a test dataframe."""
    df = generate_data_frame(
        speakers=speakers,
        genders=['M', 'F'],
        factors=dict(
            group=['HV', 'LV'],
            test=['pre', 'post'],
            vowel=['a', 'e', 'i', 'o', 'u']))
    return df


DATA_FRAME = get_test_dataframe()


class TestBarkNormalizer(Helper.TestFormantNormalizerBase):
    """
    Tests for the BarkNormalizer.
    """
    normalizer = BarkNormalizer
    transform = hz_to_bark


class TestErbNormalizer(Helper.TestFormantNormalizerBase):
    """
    Tests for the ErbNormalizer.
    """
    normalizer = ErbNormalizer
    transform = hz_to_erb


class TestLog10Normalizer(Helper.TestFormantNormalizerBase):
    """
    Tests for the Log10Normalizer.
    """
    normalizer = Log10Normalizer
    transform = np.log10


class TestLogNormalizer(Helper.TestFormantNormalizerBase):
    """
    Tests for the LogNormalizer.
    """
    normalizer = LogNormalizer
    transform = np.log


class TestMelNormalizer(Helper.TestFormantNormalizerBase):
    """
    Tests for the MelNormalizer.
    """
    normalizer = MelNormalizer
    transform = hz_to_mel
