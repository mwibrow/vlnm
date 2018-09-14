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

class TestColumnValidationPasses(unittest.TestCase):
    """
    Check columns are in data frame
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

    def test_choice_column_alias(self):
        """
        Choice column alias present in data frame.
        """
        df = self.df.copy()[['participant', 'f0@50']]
        valid = validate_required_columns(
            self.normalizer,
            df,
            ['speaker'],
            dict(speaker='participant'))
        self.assertTrue(valid)

class TestColumnValidationErrors(unittest.TestCase):
    """
    Check missing columns raises errors
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


class TestKeywordValidationPasses(unittest.TestCase):
    """
    Check keyword arguments are provided.
    """

    def setUp(self):
        self.normalizer = 'test-normalizer'

    def test_required_keyword(self):
        """
        Required keyword passes.
        """
        valid = validate_required_keywords(
            self.normalizer,
            ['method'],
            dict(method='method1'))
        self.assertTrue(valid)

    def test_choice_keyword(self):
        """
        Choice keywords passes.
        """
        valid = validate_choice_keywords(
            self.normalizer,
            ['female', 'male'],
            dict(female='F'))
        self.assertTrue(valid)

class TestKeywordValidationErrors(unittest.TestCase):
    """
    Check missing keywords raises errors
    """

    def setUp(self):
        self.normalizer = 'test-normalizer'

    def test_required_keyword_missing(self):
        """
        Missing required keyword raises error.
        """
        with self.assertRaises(RequiredKeywordMissingError):
            validate_required_keywords(
                self.normalizer,
                ['method'],
                dict())

    def test_choice_keyword_missing(self):
        """
        Missing choice keywords raises error.
        """
        with self.assertRaises(ChoiceKeywordMissingError):
            validate_choice_keywords(
                self.normalizer,
                ['female', 'male'],
                dict())
