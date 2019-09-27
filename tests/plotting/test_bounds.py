"""
Tests for the bounds module
~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import unittest

import numpy as np

from vlnm.plotting.bounds import BoundingBox


class TestBoundingBox(unittest.TestCase):
    """Tests for the BoundingBox class."""

    def test_initialise(self):
        """Initialise without error."""
        BoundingBox()

    def test_update_with_xy(self):
        """Do not using xy argument."""
        box = BoundingBox()
        xy = np.array([[0, 1], [2, 3]])
        box.update_from_xy(xy)
        self.assertTrue(np.all(box.box == xy))

    def test_update_with_x_y(self):
        """Do not using x and y arguments."""
        box = BoundingBox()
        xy = np.array([[0, 1], [2, 3]])
        x, y = xy[:, 0], xy[:, 1]
        box.update_from_xy(x=x, y=y)
        self.assertTrue(np.all(box.box == xy))

    def test_no_update_xy(self):
        """Do not update if points are within current bounds."""
        box = BoundingBox()
        xy = np.array([[0, 10], [20, 30]])
        box.update_from_xy(xy)
        box.update_from_xy(np.array([[1, 11], [19, 29]]))
        self.assertTrue(np.all(box.box == xy))

    def test_do_update_xy(self):
        """Do update if points are outside current bounds."""
        box = BoundingBox()
        xy1 = np.array([[0, 10], [20, 30]])
        box.update_from_xy(xy1)
        xy2 = np.array([[1, 19], [21, 31]])
        box.update_from_xy(xy2)

        xy3 = np.vstack((xy1[0, :], xy2[1, :]))
        self.assertTrue(np.all(box.box == xy3))

    def test_initial_lower(self):
        """Lower bound should be None after initialisation."""
        self.assertIsNone(BoundingBox().lower())

    def test_initial_upper(self):
        """Get upper bound after initialisation."""
        self.assertIsNone(BoundingBox().upper())

    def test_lower(self):
        """Get lower bound after update."""
        box = BoundingBox()
        xy = np.array([[0, 10], [20, 30]])
        box.update_from_xy(xy)
        self.assertTrue(np.all(box.lower() == xy[0, :]))

    def test_upper(self):
        """Get upper bound after update."""
        box = BoundingBox()
        xy = np.array([[0, 10], [20, 30]])
        box.update_from_xy(xy)
        self.assertTrue(np.all(box.upper() == xy[1, :]))
