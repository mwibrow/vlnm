"""
Tests for the `artists` module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import unittest

from vlnm.plotting.artists import (
    dict_diff,
    Artist
)


class TestDictDiff(unittest.TestCase):
    """Tests for the dict_dict function"""

    def test_empty_dicts(self):
        """Empty dicts returns empty dict"""
        self.assertDictEqual({}, dict_diff({}, {}))

    def test_diff(self):
        """Remove common keys"""
        self.assertDictEqual({'a': 1}, dict_diff({'a': 1, 'b': 2}, {'b': 2}))


class TestArtist(unittest.TestCase):
    """Tests for the Artist class"""

    def test_init_no_defaults(self):
        """No defaults assigns empty dict"""
        artist = Artist()
        self.assertDictEqual(artist.defaults, {})

    def test_init_class_defaults(self):
        """No defaults assigns class defaults"""
        expected = dict(a=1, b=2)

        class FakeArtist:
            defaults = expected

        artist = FakeArtist()
        self.assertDictEqual(artist.defaults, expected)

    def test_init_custom_defaults(self):
        """Defaults assigned correctly"""
        expected = dict(a=1, b=2)

        artist = Artist(defaults=expected)
        self.assertDictEqual(artist.defaults, expected)
