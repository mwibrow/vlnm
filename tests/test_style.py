"""
tests for the vlnm.plotting.style module
"""

import unittest

from vlnm.plotting import style

class TestGetGroupStyle(unittest.TestCase):
    """Tests for the get_group_style function."""

    def test_no_groups(self):
        """No groups returns empty style."""
        expected = {}
        actual = style.get_group_styles(
            [], ('had',), dict(color='vowel'), dict(color=dict(had='black')))
        self.assertEqual(actual, expected)

    def test_no_values(self):
        """No values returns empty style."""
        expected = {}
        actual = style.get_group_styles(
            ['vowel'], (), dict(color='vowel'), dict(color=dict(had='black')))
        self.assertEqual(actual, expected)

    def test_single_style(self):
        """Correct style returned."""
        expected = dict(color='blue')
        actual = style.get_group_styles(
            ['vowel'], ('had',),
            dict(color='vowel'), dict(color=dict(had='blue')))
        self.assertEqual(actual, expected)

    def test_multilples_styles(self):
        """Correct styles returned."""
        expected = dict(color='blue', marker='.', line='-')
        actual = style.get_group_styles(
            ['vowel', 'gender', 'participant'], ('had', 'F', 'S1'),
            dict(color='vowel', marker='gender', line='participant'),
            dict(
                color=dict(had='blue'),
                marker=dict(F='.'),
                line=dict(S1='-')))
        self.assertEqual(actual, expected)
