"""
    Plotting utilities
    ~~~~~~~~~~~~~~~~~~

"""

from typing import Iterable, List, Tuple, Union

from matplotlib.figure import Figure
import matplotlib.patches as mpatches
from matplotlib.legend_handler import HandlerPatch
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as st


def create_figure(*args, **kwargs) -> Figure:
    """Wrapper around matplotlib.pyplot.figure"""
    return plt.figure(*args, **kwargs)


class HandlerEllipse(HandlerPatch):
    def create_artists(
            self, legend, orig_handle,
            xdescent, ydescent, width, height, fontsize, transform):
        center = (width - xdescent) / 2, (height - ydescent) / 2
        patch = mpatches.Ellipse(
            xy=center, width=(width + xdescent),
            height=height + ydescent)
        self.update_prop(patch, orig_handle, legend)
        patch.set_transform(transform)
        return [patch]


def get_confidence_ellipse(
        x: List[float],
        y: List[float],
        confidence: float = 0.95,
        n_std: float = None,
        n_mad: float = None) -> Tuple[float, float, float]:
    """Calculate parameters for a 2D 'confidence ellipse'

    Parameters
    ----------
    x:
        Data for the x-coordinates.
    y:
        Data for the y-coordinates.
    confidence:
        Confidence level in the range :math:`0` to :math:`1`
        used to determine the major and minor axis of the ellipse.
        Ignored if either of the ``n_std`` or ``n_mad` parameters are given.
    n_std:
        If specified, the number of standard deviations from the mean used
        used to determine the major and minor axis of the ellipse.
    n_mad:
        If specified, the number of median absolute deviations from the median used
        used to determine the major and minor axis of the ellipse.
        In addition the ellipse will be centered at the median
        of the data points.

    Returns
    -------
    :
        A 5-tuple containing the x- and y- cooridnates of the center,
        (horizontal) width, (vertical) height, and angle (in degrees)
        of the required ellipse.
    """
    x = np.array(x)
    y = np.array(y)
    if x.size != y.size:
        raise ValueError('Ellipse data must be the same shape.')
    if x.size < 3 or y.size < 3:
        raise ValueError('Too little data to calculate ellipse')
    cov = np.cov(x, y)
    eigenvalues, eignvectors = np.linalg.eig(cov)
    angle = np.arctan2(*np.flip(eignvectors[:, 0]))

    if n_mad:
        cx, cy = np.median(x), np.median(y)
    else:
        cx, cy = np.mean(x), np.mean(y)

    if n_mad:
        x, y = rotate_xy(x - cx, y - cy, angle)
        width, height = rotate_xy(2 * np.median(x) * n_mad, 2 * np.median(y) * n_mad, -angle)
    if n_std:
        x, y = rotate_xy(x - cx, y - cy, angle)
        width, height = rotate_xy(2 * np.std(x) * n_std, 2 * np.std(y) * n_std, -angle)
    else:
        alpha = st.chi2(df=2).ppf(confidence)
        width, height = 2 * np.sqrt(alpha * eigenvalues)

    angle = angle / np.pi * 180
    return cx, cy, width, height, angle


def rotate_xy(
        x: Union[Iterable[float], float],
        y: Union[Iterable[float], float],
        angle: float) -> Tuple[np.array, np.array]:
    """Rotate 2d coordinates.

    Paramaters
    ----------
    x:
        Data x-coordinates.
    y:
        Data y-coordinates.
    angle:
        Angle to rotate in radians.

    Returns
    -------
    :
        A 2-tuple containing the rotated coordinates.
    """
    cs, sn = np.cos(angle), np.sin(angle)
    matrix = np.matrix([[cs, -sn], [sn, cs]])
    x, y = np.asarray(matrix.dot([np.atleast_1d(x), np.atleast_1d(y)]))
    return x, y


def aggregate_df(
        df: pd.DataFrame,
        columns: List[str],
        groups: List[str] = None,
        where: Union[str, None] = None) -> pd.DataFrame:
    """Aggregate dataframe columns over grouping factors.

    """
    if where and groups:
        if where == 'mean':
            df = df.groupby(groups, as_index=True).apply(
                lambda group_df: group_df[columns].mean(axis=0))
            df = df.reset_index()
        elif where == 'median':
            df = df.groupby(groups, as_index=True).apply(
                lambda group_df: group_df[columns].median(axis=0))
            df = df.reset_index()
        df = df[df[columns].apply(np.isfinite).apply(np.all, axis=1)]
    return df
