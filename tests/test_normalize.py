"""
Test for the normalize module.
"""

import unittest

import pandas as pd

from vlnm.normalize import (
    check_columns,
    update_options
)

class TestCheckColumns(unittest.TestCase):
    """
    Tests for the check_columns function.
    """

    def setUp(self):
        self.df = pd.DataFrame(dict(
            speaker=['speaker1', 'speaker2', 'speaker3'],
            gender='gender',
            f0=[50, 100, 150],
            f1=[350, 400, 450],
            f2=[750, 800, 850]))

    def test_required_column_no_alias_error(self):
        """
        Error if required column not in data frame.
        """
        with self.assertRaises(ValueError):
            check_columns(
                self.df,
                dict(required=['vowel']),
                {},
                [])

    def test_required_aliased_column_error(self):
        """
        Error if required alised column not in data frame.
        """
        with self.assertRaises(ValueError):
            check_columns(
                self.df,
                dict(required=['vowel']),
                dict(vowel='word'),
                [])

    def test_choice_columns_error(self):
        """
        Error if one of a choice column is not in data frame.
        """
        with self.assertRaises(ValueError):
            check_columns(
                self.df,
                dict(required=[], formants=['f3']),
                {},
                [])

    def test_choice_column_aliased_error(self):
        """
        Error if an aliased choicecolumn is not in data frame.
        """
        with self.assertRaises(ValueError):
            check_columns(
                self.df,
                dict(required=[], formants=['f3']),
                dict(f3='f3@50'),
                [])

    def test_formant_column_error(self):
        """
        Error if an invalid formant is given.
        """
        with self.assertRaises(ValueError):
            check_columns(
                self.df,
                dict(required=[], formants=['fk']),
                {},
                [])

    def test_group_column_error(self):
        """
        Error if a grouping column is not in the data frame.
        """
        with self.assertRaises(ValueError):
            check_columns(
                self.df,
                dict(required=[]),
                {},
                ['test'])

    def test_group_column_aliased_error(self):
        """
        Error if an aliased grouping column is not in the data frame.
        """
        with self.assertRaises(ValueError):
            check_columns(
                self.df,
                dict(required=[]),
                dict(test='other'),
                ['test'])