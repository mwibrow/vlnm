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
                dict(required=[], choice=dict(
                    formants=['f3']
                )),
                {},
                [])

    def test_choice_column_aliased_error(self):
        """
        Error if an aliased choicecolumn is not in data frame.
        """
        with self.assertRaises(ValueError):
            check_columns(
                self.df,
                dict(required=[], choice=dict(
                    formants=['f3']
                )),
                dict(f3='f3@50'),
                [])

    def test_formant_column_error(self):
        """
        Error if an invalid formant is given.
        """
        with self.assertRaises(ValueError):
            check_columns(
                self.df,
                dict(required=[], choice=dict(
                    formants=['fk']
                )),
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


class TestUpdateOptions(unittest.TestCase):
    """
    Tests for the update_options function.
    """

    def setUp(self):
        self.column_specs = dict(
            required=['speaker', 'vowel'],
            formants=['f0', 'f1', 'f2', 'f3'])
        self.column_alias = dict(
            spekaer='partiticant',
            vowel='ipa')

    def test_update_options(self):
        """
        Update options from column_specs
        """
        options = {}
        update_options(options, self.column_alias, self.column_specs)
        self.assertTrue(dict(vowel='ipa').items() <= options.items())

    def test_update_column_alias(self):
        """
        Update column_alias from options
        """
        options = dict(f0='f0@50')
        update_options(options, self.column_alias, self.column_specs)
        self.assertTrue(options.items() <= self.column_alias.items())
