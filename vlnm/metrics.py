"""
Metrics
~~~~~~~
"""

import shapely


def vowel_space(
        df, speaker='speaker', vowel='vowel',
        apices=None, formants=('f1', 'f2')):
    """Calculate the vowel space area by speaker.

    Parameters
    ----------

    df : :class:`pandas.DataFrame`
        Formant data.
    speaker : :obj:`str`
        Data-frame column which contains the speaker labels.
    vowel : :obj:`str`
        Data-frame column which contains the vowel labels.
    apices : :obj:`list`
        List of vowel labels to use as the apices of the vowel space.
        If not provided, all vowels will be used.
    formants :obj:`tuple`

    Return
    ------

    """

def scv(df, speaker='speaker'):
    """
    Squared coefficient of variation
    """
