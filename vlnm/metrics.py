"""
Metrics
~~~~~~~
"""

from scipy.spatial import ConvexHull
from shapely.geometry import Polygon

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
    means = df[subset].groupby(vowel).mean()
    hull = ConvexHull(means.as_matrix())
    polygon = Polygon([df.loc[vertex, formants] for vertex in hull.vertices])
    return polygon.area


def scv(df, speaker='speaker'):
    """
    Squared coefficient of variation
    """
