"""
Tests for the base module
"""

from vlnm.normalizers.base import Normalizer

from tests.helpers import Helper


class TestNormalizer(Helper.TestNormalizerBase):
    """
    Tests for the base Normalizer class.
    """

    def test_config_default(self):
        """Check default config."""
        expected = dict(columns=[], keywords=[], options=dict())
        actual = self.normalizer()
        self.assertDictEqual(actual.config, expected)


    def test_config_merged(self):
        """Check config merged in sublacss."""

        class Subclass(Normalizer):
            """Test sub-class."""
            config = dict(options=dict(transform=True))

        expected = dict(columns=[], keywords=[], options=dict(transform=True))
        actual = Subclass()
        self.assertDictEqual(actual.config, expected)
