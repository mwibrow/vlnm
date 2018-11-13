"""
Metrics
~~~~~~~

The :module:`vlnm.metrics` module provides metrics
for evaluating normalization methods.
"""

import pandas as pd
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon


def vowel_space(
        df, vowel='vowel', apices=None, formants=('f1', 'f2'), hull=True):
    """Calculate the vowel space for a speaker.

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

    hull : :obj:`bool`
        If :code:`True` (the default) a convex hull will be
        fitted mean formant data for the apices, prior
        to calculating the polygon exterior.

    Return
    ------
    :obj:`shapely.geometry.Polygon`
        Vowel space represented as a Polygon.
    """
    if apices:
        df = df[df[vowel].isin(apices)]
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
        df, speaker='speaker', vowel='vowel',
        apices=None, formants=('f1', 'f2')):
    """Squared coefficient of variation for vowel spaces.

    Parameters
    ----------

    df : :class:`pandas.DataFrame`
        Formant data for all speakers.

    speaker : :obj:`str`
        Data-frame column which contains the speaker labels.
        Defaults to :code:`'speaker'`.

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
        Square coefficient of variation for the vowel space.
    """
    def _area(group_df):
        return pd.DataFrame(dict(
            speaker=group_df['speaker'].unique(),
            area=vowel_space(
                group_df, vowel=vowel, apices=apices, formants=formants).area
        ))
    areas_df = df.groupby(speaker, as_index=False).apply(_area)
    return (areas_df.std() / areas_df.mean()) ** 2