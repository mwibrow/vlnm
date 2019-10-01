"""
Tests for the vlnm.plotting.legends module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import unittest

from vlnm.plotting.legends import (
    Legend,
    LegendCollection,
    LegendGroup,
    translate_legend_options,
    TRANSLATOR,
)


class TestTranslateLegendOptions(unittest.TestCase):
    """Tests for the translate_legend_options function."""

    def test_no_options(self):
        """No options returns empty dict."""
        options = translate_legend_options()
        self.assertDictEqual(options, {})

    def test_no_translation(self):
        """Non-translatable options returned unchanged."""
        expected = dict(a=1, b=2)
        actual = translate_legend_options(**expected)
        self.assertDictEqual(actual, expected)

    def test_translate_position(self):
        """Position option translated."""
        expected = dict(a=1, b=2, **TRANSLATOR['position']['bottom'])
        actual = translate_legend_options(a=1, b=2, position='bottom')
        self.assertDictEqual(actual, expected)

    def test_translate_invalid_position(self):
        """Invalid position option raises error."""
        with self.assertRaises(ValueError):
            translate_legend_options(position='INVALID')
