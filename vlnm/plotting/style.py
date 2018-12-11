"""
Module for handling plotting 'styles'.

A plotting style is a specification of how graphical parameters
such as color, plot marker or line style vary with the plotting
data.

In almost all cases, the graphical parameters should reflect changes
in _categorical_ data (e.g., vowel category, reported gender, or particiant id).
"""

from typing import Any, Dict, List, Tuple, Union

import matplotlib.colors

from matplotlib.cm import get_cmap
from matplotlib import Path
from matplotlib.font_manager import FontProperties
# pylint: disable=C0103
Color = Union[str, Tuple[float, float, float, float]]
Colormap = Dict[any, Color]
Colors = Union[List[Color], matplotlib.colors.ListedColormap]
Line = Union[str, List[int]]
Lines = Union[Dict[str, Line], List[Line]]
Marker = Union[str, Tuple[int, int, int], List[Tuple[float, float]], Path]
Markers = List[Marker]
Font = Union[str, FontProperties]
Fonts = Union[Dict[str, Font], List[Font]]

STYLES = dict(
    default=dict(
        color='black',
        marker='.',
        line='-'
    )
)

def get_group_styles(
        groups: List[str],
        values: Tuple[Any],
        vary: Dict[str, str],
        style_maps: Dict[str, dict]) -> Dict[str, Any]:
    """Get the style for a group of observations.

    Parameters
    ----------
    groups:
        The list of Dataframe columns used to split a Dataframe.
    values:
        The data values for a particular group. This will be the first
        item in the tuple generated when iterating over a
        `Dataframe.groupby` generator.
    vary:
        A dictionary mapping style properties onto Dataframe columns.
    style_maps:
        Mappings for style properties from data values to graphical properties.

    Returns
    -------
    :
        The plotting styles for the group with the specified values.
    """
    if not groups or not values:
        return {}
    yrav = {}
    for prop, column in vary.items():
        yrav[column] = yrav.get(column, set())
        yrav[column].add(prop)

    style = {}
    for column, value in zip(groups, values):
        try:
            for prop in yrav[column]:
                style_map = style_maps.get(prop)
                if style_map and value in style_map:
                    style[prop] = style_map[value]
        except KeyError:
            pass
    return style

def get_color_cycle(colors: Colors) -> List[Color]:
    """Generate a color cycle.
    """
    if isinstance(colors, (list, dict)):
        return colors
    elif isinstance(colors, matplotlib.colors.Colormap):
        return list(colors.colors)
    else:
        try:
            return list(get_cmap(colors).colors)
        except ValueError:
            return [colors]

def get_color_list(colors: Colors, levels: int = 1) -> List[Color]:
    """Generate a list of colors.

    colors:
        The source of the color list.
        - :obj:`str` name of a color map
        - :obj:`str` name of a color
        - :obj:`tuple` of :obj:`float` repesenting an RGBA color
        - :obj:`list` a list of colors
    levels:
        The number of levels in the color list.
    """
    if isinstance(colors, list):
        return colors[:levels]
    elif isinstance(colors, matplotlib.colors.Colormap):
        cmap = colors
        if len(cmap.colors) != levels:
            cmap = get_cmap(colors.name, lut=levels)
        return list(cmap.colors)
    else:
        try:
            cmap = get_cmap(colors, lut=levels)
            if len(cmap.colors) != levels:
                cmap = get_cmap(cmap.name, lut=levels)
            return list(cmap.colors)
        except ValueError:
            return [colors]

def get_color_map(
        colors: Colors, categories: List[str]) -> Dict[str, Color]:
    """Get a category-color mapping.

    Parameters
    ----------
    colors:
        Color specification.
    categories:
        A list of (vowel) categories.

    Returns
    -------
    :
        A dictionary mapping category labels to colors.
    """
    if isinstance(colors, dict):
        return colors
    color_list = get_color_list(colors, len(categories))
    if not color_list:
        color_list = [None for _ in categories]
    color_map = {}
    for i, category in enumerate(categories):
        color_map[category] = color_list[i % len(color_list)]
    return color_map

def get_marker_map(
        markers: Markers, categories: List[str]) -> Dict[str, Marker]:
    """Get a category-marker mapping.

    Parameters
    ----------
    markers:
        Marker specification.
    categories:
        A list of (vowel) categories.

    Returns
    -------
    :
        A dictionary mapping category labels to markers.
    """
    if isinstance(markers, dict):
        return markers
    if isinstance(markers, list):
        marker_list = markers
    else:
        marker_list = [markers]

    if not marker_list:
        marker_list = [None]

    marker_map = {}
    for i, category in enumerate(categories):
        marker_map[category] = marker_list[i % len(marker_list)]
    return marker_map

def get_marker_cycle(markers):
    """Create a marker cycle."""
    if isinstance(markers, (dict, list)):
        return markers
    return [markers]


def get_line_map(
        lines: Lines, categories: List[str]) -> Dict[str, Line]:
    """Get a category-marker mapping.

    Parameters
    ----------
    Lines:
        Marker specification.
    categories:
        A list of (vowel) categories.

    Returns
    -------
    :
        A dictionary mapping category labels to markers.
    """
    if isinstance(lines, dict):
        return lines
    if isinstance(lines, list):
        line_list = lines
    else:
        line_list = [lines]

    if not line_list:
        line_list = [None]

    line_map = {}
    for i, category in enumerate(categories):
        line_map[category] = line_list[i % len(line_list)]
    return line_map
