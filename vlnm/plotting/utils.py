"""
    Plotting utilities
    ~~~~~~~~~~~~~~~~~~

"""
from functools import reduce
from typing import Callable, Dict, Iterable, List, Tuple, Union

from matplotlib.figure import Figure
import matplotlib.patches as mpatches
from matplotlib.legend_handler import HandlerPatch
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as st

from vlnm.utils import merge, strip


def create_figure(*args, **kwargs) -> Figure:
    """Wrapper around matplotlib.pyplot.figure"""
    return plt.figure(*args, **kwargs)


def translate_props(props: Dict, translator: Dict[str, Union[str, Iterable, Callable]]) -> Dict:
    """
    Translate from user-supplied properties to internal properties.

    Parameters
    ----------
    props:
        Dictionary of properties.
    translator:
        Dictionary mapping property names to one or more property names,
        or a function to return multiple properties as a dictionary.

    Returns
    -------
    :
        Dictionary of translated properties.
    """
    translated = {}
    for prop, value in props.items():
        if prop in translator:
            translation = translator[prop]
            try:
                translated.update(**translation(value))
            except TypeError:
                if isinstance(translation, list):
                    translated.update(**{key: value for key in translation})
                else:
                    translated[translation] = value
        else:
            translated[prop] = value
    return translated


def context_from_kwargs(
        kwargs: Dict,
        include: List[str] = None,
        exclude: List[str] = None) -> Tuple[Dict, Dict]:
    r"""
    Separate context and non-context keyword arguments.

    Parameters
    ----------
    \*\*kwargs:
        Keyword arguments.
    include:
        Keywords that are always in the context.
    exclude:
        Keywords that are never in the context.

    Returns
    -------
    :
        The context keywords and the rest.

    """
    include = include or []
    exclude = exclude or []

    context = {}
    rest = kwargs.copy()
    for key, value in kwargs.items():
        if key in include:
            context[key] = value
            del rest[key]
        elif key in exclude:
            continue
        elif key.endswith('_by'):
            context[key] = value
            del rest[key]
            prop = key[:-3]
            if prop in kwargs:
                context[prop] = kwargs[prop]
                del rest[prop]

    context = strip(context)
    return context, rest


def merge_contexts(*contexts):
    return reduce(merge, contexts)


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
    elif x.size < 3 or y.size < 3:
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
