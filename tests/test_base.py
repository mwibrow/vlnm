"""
Tests for the base module
"""

from vlnm.normalizers.base import (
    FormantGenericNormalizer,
    FormantSpecificNormalizer,
    FormantsTransformNormalizer,
    Normalizer)

from tests.helpers import Helper


class TestBaseNormalizers(Helper.TestNormalizerBase):
    """
    Tests for the base Normalizer class.
    """

    def test_normalizer_instantiation(self):
        """Base Normalizer class cannot be instantiated"""
        with self.assertRaises(TypeError):
            Normalizer()

    def test_formant_generic_normalizer_instantiation(self):
        """Base FormantGenericNormalizer class cannot be instantiated"""
        with self.assertRaises(TypeError):
            FormantGenericNormalizer()

    def test_formant_specific_normalizer_instantiation(self):
        """Base FormantsSpecificNormalizer class cannot be instantiated"""
        with self.assertRaises(TypeError):
            FormantSpecificNormalizer()

    def test_formant_transform_normalizer_instantiation(self):
        """Base FormantsTransformNormalizer class cannot be instantiated"""
        with self.assertRaises(TypeError):
            FormantsTransformNormalizer()

    def test_config_default(self):
        """Check default config"""
        expected = dict(columns=[], keywords=[], options=dict(), outputs=[])
        actual = self.normalizer()
        self.assertDictEqual(actual.config, expected)

    def test_config_merged(self):
        """Check config merged in subclass"""

        class Subclass(Normalizer):
            """Test sub-class"""
            config = dict(options=dict(transform=True))

        expected = dict(columns=[], keywords=[], options=dict(transform=True), outputs=[])
        actual = Subclass()
        self.assertDictEqual(actual.config, expected)
