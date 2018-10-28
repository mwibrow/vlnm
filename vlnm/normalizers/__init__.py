"""
    Normalizers package.
    ~~~~~~~~~~~~~~~~~~~~

    .. autofunction:: normalize
"""

from vlnm.normalizers.normalizers import (
    BarkDifferenceNormalizer,
    BarkNormalizer,
    BighamNormalizer,
    BladenNormalizer,
    ErbNormalizer,
    GerstmanNormalizer,
    LCENormalizer,
    LobanovNormalizer,
    Log10Normalizer,
    LogNormalizer,
    MelNormalizer,
    NearyGMNormalizer,
    NearyNormalizer,
    NordstromNormalizer,
    SchwaNormalizer,
    VowelNormalizer,
    WattFabricius2Normalizer,
    WattFabricius3Normalizer,
    WattFabriciusNormalizer)

NORMALIZERS = {}

def register_normalizer(klass, *aliases):
    """Register a normalizer class."""
    for alias in aliases:
        NORMALIZERS[alias] = klass

register_normalizer(BarkDifferenceNormalizer,
    'bark_difference', 'bark_diff')
register_normalizer(BarkNormalizer, 'bark')
register_normalizer(LobanovNormalizer, 'lobanov', 'lob')

def normalize(df, *args, method=None, **kwargs):
    """Normalize vowel data in a pandas dataframe.

    """
    try:
        return method.normalize(df, *args, **kwargs)
    except AttributeError:
        try:
            return method().normalize(df, *args, **kwargs)
        except TypeError:
            return NORMALIZERS[method]().normalize(
                df, *args, **kwargs)
