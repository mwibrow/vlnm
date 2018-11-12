"""
Metrics
~~~~~~~
"""

from scipy.spatial import ConvexHull
from shapely.geometry import Polygon

def polygon_area(points, hull=True):
    """Calculate the area of a polygon.

    Parameters
    ----------

    points : :obj:`list` of :obj:`tuple`
        A list of tuples, with each tuple representing
        a point.
        Note, that any data structure can be used
        that can be indexex similarly (e.g., :class:`numpy.ndarray`).

    hull : :obj:`bool`
        If true (the default) the convex hull of the points
        will be calculated first using :class:`scipy.spatial.ConvexHull`.

    Return
    ------
    :obj:`float`
        The area of the polygon.
    """
    if hull:
        convex_hull = ConvexHull(points)
        polygon = Polygon([points[vertex] for vertex in convex_hull.vertices])
    else:
        polygon = Polygon(points)
    return polygon.area

def vowel_space_area(
        df, vowel='vowel', apices=None, formants=('f1', 'f2')):
    """Calculate the vowel space area for a speaker.

    Parameters
    ----------

    df : :class:`pandas.DataFrame`
        Formant data for a `single` speaker.

    vowel : :obj:`str`
        Data-frame column which contains the vowel labels.
        Defaults to :code:`'vowel'`.

    apices : :obj:`list`
        List of vowel labels to use as the apices of the vowel space.
        If not provided, all vowels will be used.

    formants :obj:`tuple`
        The formant columns in the dataframe.
        Defaults to :code:`('f1', 'f2')`.

    Return
    ------
    :obj:`float`
        Area of the vowel space.
    """
    if apices:
        df = df[df[vowel].isin(apices)]
    subset = [vowel]
    subset.extend(formants)
    means = df[subset].groupby(vowel).mean().as_matrix()
    return polygon_area(means)


def scv(df, speaker='speaker'):
    """
    Squared coefficient of variation
    """
