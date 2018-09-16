"""
Tests for the conversion module.
"""

import unittest

import numpy as np

from vlnm.conversion import (
    hz_to_bark,
    hz_to_erb,
    hz_to_mel)


class TestHzToBark(unittest.TestCase):
    """
    Test the hz_to_bark function.
    """

    def setUp(self):
        self.convert = lambda frq: 26.81 * frq / (frq + 1960) - 0.53

    def test_hz_to_bark_number(self):
        """Test single number."""
        data = np.random.randn(1)[0]
        expected = self.convert(data)
        actual = hz_to_bark(data)
        self.assertEqual(expected, actual)

    def test_hz_to_bark_vector(self):
        """Test vector."""
        data = np.random.randn(100)
        expected = self.convert(data)
        actual = hz_to_bark(data)
        self.assertTrue(np.array_equal(expected, actual))

    def test_hz_to_bark_matrix(self):
        """Test matrix."""
        data = np.random.randn(3, 100)
        expected = self.convert(data)
        actual = hz_to_bark(data)
        self.assertTrue(np.array_equal(expected, actual))


class TestHzToErb(unittest.TestCase):
    """
    Test the hz_to_erb function.
    """

    def setUp(self):
        self.convert = lambda frq: 21.4 * np.log(1 + 0.00437 * frq)

    def test_hz_to_erb_number(self):
        """Test single number."""
        data = np.random.randn(1)[0]
        expected = self.convert(data)
        actual = hz_to_erb(data)
        self.assertEqual(expected, actual)

    def test_hz_to_erb_vector(self):
        """Test vector."""
        data = np.random.randn(100)
        expected = self.convert(data)
        actual = hz_to_erb(data)
        self.assertTrue(np.array_equal(expected, actual))

    def test_hz_to_erb_matrix(self):
        """Test matrix."""
        data = np.random.randn(3, 100)
        expected = self.convert(data)
        actual = hz_to_erb(data)
        self.assertTrue(np.array_equal(expected, actual))


class TestHzToMel(unittest.TestCase):
    """
    Test the hz_to_mel function.
    """

    def setUp(self):
        self.convert = lambda frq: 1127. * np.log(1. + frq / 700.)

    def test_hz_to_mel_number(self):
        """Test single number."""
        data = np.random.randn(1)[0]
        expected = self.convert(data)
        actual = hz_to_mel(data)
        self.assertEqual(expected, actual)

    def test_hz_to_mel_vector(self):
        """Test vector."""
        data = np.random.randn(100)
        expected = self.convert(data)
        actual = hz_to_mel(data)
        self.assertTrue(np.array_equal(expected, actual))

    def test_hz_to_mel_matrix(self):
        """Test matrix."""
        data = np.random.randn(3, 100)
        expected = self.convert(data)
        actual = hz_to_mel(data)
        self.assertTrue(np.array_equal(expected, actual))
