"""
Tests for the validation module
"""
# pylint: disable=invalid-name

import unittest

import pandas as pd

from vlnm.decorators import (
    Columns,
    Keywords,
    Returns)
from vlnm.validation import (
    ChoiceColumnAliasMissingError,
    ChoiceColumnMissingError,
    ChoiceKeywordMissingError,
    RequiredColumnAliasMissingError,
    RequiredColumnMissingError,
    RequiredKeywordMissingError,
    validate_choice_columns,
    validate_choice_keywords,
    validate_columns,
    validate_keywords,
    validate_required_columns,
    validate_required_keywords)

class TestValidationPasses(unittest.TestCase):
    """
    Check columns/keywords are in data frame
    """

    def setUp(self):
        self.df = pd.DataFrame({
            'speaker': ['speaker1', 'speaker2'],
            'participant': ['participant1', 'participant2'],
            'f0': [100, 200],
            'f0@50': [150, 250]
        })
        self.normalizer = 'test-normalizer'

    def test_required_column(self):
        """
        Required column present in data frame.
        """
        df = self.df.copy()[['speaker', 'f0']]
        valid = validate_required_columns(
            self.normalizer,
            df,
            ['speaker'],
            {})
        self.assertTrue(valid)

    def test_required_column_alias(self):
        """
        Required column alias present in data frame.
        """
        df = self.df.copy()[['participant', 'f0@50']]
        valid = validate_required_columns(
            self.normalizer,
            df,
            ['speaker'],
            {'speaker': 'participant'})
        self.assertTrue(valid)

    def test_choice_column(self):
        """
        Choice column present in data frame.
        """
        df = self.df.copy()[['speaker', 'f0']]
        valid = validate_required_columns(
            self.normalizer,
            df,
            ['speaker'],
            {})
        self.assertTrue(valid)

class TestValidationErrors(unittest.TestCase):
    """
    Check missing columns/keywords raises errors
    """

    def setUp(self):
        self.df = pd.DataFrame()
        self.normalizer = 'test-normalizer'

    def test_required_column_missing(self):
        """
        Required column missing in data frame raises error.
        """
        with self.assertRaises(RequiredColumnMissingError):
            validate_required_columns(
                self.normalizer,
                self.df,
                ['speaker'],
                {})

    def test_required_column_alias_missing(self):
        """
        Required alised column missing in data frame raises error.
        """
        with self.assertRaises(RequiredColumnAliasMissingError):
            validate_required_columns(
                self.normalizer,
                self.df,
                ['speaker'],
                dict(speaker='participant'))

    def test_choice_column_missing(self):
        """
        Choice column missing in data frame raises error.
        """
        with self.assertRaises(ChoiceColumnMissingError):
            validate_choice_columns(
                self.normalizer,
                self.df,
                dict(formants=['f0', 'f1', 'f2', 'f3']),
                {})

    def test_choice_column_alias_missing(self):
        """
        Choice column missing in data frame raises error.
        """
        with self.assertRaises(ChoiceColumnMissingError):
            validate_choice_columns(
                self.normalizer,
                self.df,
                dict(formants=['f0', 'f1', 'f2', 'f3']),
                dict(f0='f0@50'))
