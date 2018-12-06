"""
Module for handling plotting 'styles'.

A plotting style is a specification of how graphical parameters
such as color, plot marker or line style vary with the plotting
data.

In almost all cases, the graphical parameters should reflect changes
in _categorical_ data (e.g., vowel category, reported gender, or particiant id).
"""

from typing import Any, Dict, List, Tuple

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
                if style_map:
                    style[prop] = style_map.get(
                        value, STYLES['default'].get(prop))
        except KeyError:
            pass
    # for prop in STYLES['default']:
    #     if not prop in style:
    #         style[prop] = STYLES['default'][prop]
    return style
