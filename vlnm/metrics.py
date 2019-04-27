"""
Metrics
~~~~~~~

The `vlnm.metrics` module provides metrics
for evaluating normalization methods.
"""

import pandas as pd
from scipy.spatial import ConvexHull
import shapely
from shapely.geometry import Polygon


def vowel_space(
        df: pd.DataFrame,
        vowel: str = 'vowel',
        points: dict = None,
        formants: tuple = ('f1', 'f2'),
        hull: bool = True) -> shapely.geometry.Polygon:
    """Calculate the vowel space for a speaker.

    Parameters
    ----------

    df:
        Formant data for a `single` speaker.

    vowel:
        Data-frame column which contains the vowel labels.
        Defaults to :code:`'vowel'`.

    points:
        List of vowel labels to use as the points of the vowel space.
        If not provided, all vowels will be used.

    formants:
        The formant columns in the dataframe.
        Defaults to :code:`('f1', 'f2')`.

    hull:
        If :code:`True` (the default) a convex hull will be
        fitted mean formant data for the points, prior
        to calculating the polygon exterior.

    Returns
    -------
    :
        Vowel space represented as a Polygon.

    """
    if points:
        df = df[df[vowel].isin(points)]
    subset = [vowel]
    subset.extend(formants)
    means = df[subset].groupby(vowel).mean().as_matrix()
    if hull:
        convex_hull = ConvexHull(means)
        polygon = Polygon([means[vertex] for vertex in convex_hull.vertices])
    else:
        polygon = Polygon(means)
    return polygon


def scv(
        df: pd.DataFrame,
        vowel: str = 'vowel',
        speaker: str = 'speaker',
        points: dict = None,
        formants: tuple = ('f1', 'f2')) -> shapely.geometry.Polygon:
    """Squared coefficient of variation for vowel spaces.

    Parameters
    ----------

    df:
        Formant data for all speakers.

    speaker:
        Data-frame column which contains the speaker labels.
        Defaults to :code:`'speaker'`.

    vowel:
        Data-frame column which contains the vowel labels.
        Defaults to :code:`'vowel'`.

    points:
        List of vowel labels to use as the points of the vowel space.
        If not provided, all vowels will be used.

    formants:
        The formant columns in the dataframe.
        Defaults to :code:`('f1', 'f2')`.

    Returns
    ------
    :obj:`float`
        Square coefficient of variation for the vowel space.

    """
    def _area(group_df):
        return pd.DataFrame(dict(
            speaker=group_df[speaker].unique(),
            area=vowel_space(
                group_df, vowel=vowel, points=points, formants=formants).area
        ))
    areas_df = df.groupby(speaker, as_index=False).apply(_area)
    return (areas_df.std() / areas_df.mean()) ** 2
