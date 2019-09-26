"""
Module for bounding box management stuff
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from typing import Iterable, Union

from matplotlib.axis import Axis
import numpy as np


class BoundingBox:
    """Class representing the boundry of data."""

    def __init__(self):
        self.box = None

    def lower(self) -> np.ndarray:
        return self.box[0, :]

    def upper(self) -> np.ndarray:
        return self.box[1, :]

    def update_from_xy(
            self, xy=np.ndarray,
            x: Union[float, Iterable[float]] = None,
            y: Union[float, Iterable[float]] = None):
        if x is not None and y is not None:
            xy = np.atleast_2d([x, y]).T

        points = np.concatenate([xy, self.box]) if self.box is not None else xy
        self.box = np.vstack((
            np.min(points, axis=0),
            np.max(points, axis=0)
        ))

    def update_axis_bounds(self, axis: Axis):
        points = np.concatenate((
            np.vstack((
                axis.get_xbound(),
                axis.get_ybound(),
            )).T,
            self.box + np.ptp(self.box, axis=0) * axis.margins() * [[-1, -1], [1, 1]]
        ))
        bounds = np.vstack((
            np.min(points, axis=0),
            np.max(points, axis=0)
        ))
        axis.set_xbound(*bounds[:, 0])
        axis.set_ybound(*bounds[:, 1])

    def __repr__(self):
        return repr(self.box)
