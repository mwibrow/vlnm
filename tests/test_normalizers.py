"""
Tests for the normalizers library.
"""

import unittest

import numpy as np
import pandas as pd

from vlnm.normalizers import (
    Log10Normalizer
)


class TestLog10Normalizer(unittest.TestCase):
    """
    Tests for the Log10Normalizer class.
    """

    def test_no_columns(self):
        """
        No formant columns specified should raise ValueError.
        """

        with self.assertRaises(ValueError):
            df = pd.DataFrame(dict(
                f1=[100, 200, 300],
                f2=[1100, 1200,1300]
            ))

            normalizer = Log10Normalizer()
            normalizer.normalize(df)

    def test_basic(self):
        """
        Basic sunny day test.
        """
        df = pd.DataFrame(dict(
            f1=[100, 200, 300],
            f2=[1100, 1200, 1300]
        ))
        expected = np.log10(df.copy())

        normalizer = Log10Normalizer(f1='f1', f2='f2')
        actual = normalizer.normalize(df)

        self.assertTrue(actual.equals(expected))

    def test_new_columns(self):
        """
        Add new columns.
        """
        suffix = '_N'
        df = pd.DataFrame(dict(
            f1=[100, 200, 300],
            f2=[1100, 1200, 1300]
        ))
        expected = df.copy()
        tmp_df = np.log10(df.copy())
        tmp_df.columns = ['{}{}'.format(column, suffix) for column in tmp_df.columns]
        expected = pd.concat([df.copy(), tmp_df], axis=1)

        normalizer = Log10Normalizer(f1='f1', f2='f2', suffix=suffix)
        actual = normalizer.normalize(df)

        self.assertTrue(actual.equals(expected))
