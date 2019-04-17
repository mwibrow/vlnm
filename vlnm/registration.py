"""
Helper functions.
"""

from typing import Dict, List

from .utils import nameify

NORMALIZERS = {}


def register_normalizer(cls, *aliases: str, index: Dict = None):
    """Register a normalizer to be used with the normalize function.

    Parameters
    ----------
    cls:
        A normalizer class.
    *aliases:
        Names that can be used to refer to access the class in the
        :func:`.get_normalizer` function.
    index:
        A dictionary in which the normalizer class will be registered.
        If omitted, the global index will be used.
    """
    index = NORMALIZERS if index is None else index
    for alias in aliases:
        index[alias] = cls


def register(name: str):
    """Decorator for registering a normalizer class.

    Parameters:
        name:
            The name to use for the class.
            Internally, the :func:`.register_normalizer`
            function is called:

    Example
    -------

    .. code::

        @register('custom-normalizer')
        class CustomNormalizer(Normalizer):
            # Custom normalizer definition.
    """
    def _decorator(cls):
        register_normalizer(cls, name)
        setattr(cls, 'name', name)
        return cls
    return _decorator


def classify(vowel: str = None, formant: str = None, speaker: str = None):
    """Decorator for classifying a normalizer class.

    This adds ``classify`` attribute to the class
    consisting of a dictionary containing the keys and values
    passed to the decorator.

    This is used solely for documenting normalizers.

    Example
    -------

    .. code::

        @classify(vowel='extrinsic', formant='intrinsic', speaker='intrinsic')
        class WattFabriciusNormalizer(CentroidNormalizer):
            # Rest of definition.
    """
    def _decorator(cls):
        setattr(cls, 'classify', dict(
            vowel=vowel, formant=formant, speaker=speaker))
        return cls
    return _decorator


def get_normalizer(name: str, index: Dict = None):
    """Return a normalizer class.

    Parameters
    ----------
    name:
        The name which was used to register the normalizer
        class using :func:`.register_normalizer()`.
    index:
        The register in which the normalizer was registered.

    Returns
    -------
        The normalizer class.
    """
    index = index or NORMALIZERS
    index_lower = {key.lower(): key for key in index}
    raw = name
    name = name.lower()
    if name:
        normalizers = [item for item in index_lower
                       if item.startswith(name)]
        if normalizers:
            if len(normalizers) == 1:
                return index[index_lower[normalizers[0]]]
            if name in normalizers:
                return index[index_lower[name]]
            raise NameError(
                'Found {count} normalizers matching {name}:'
                '{matching}'.format(
                    count=len(normalizers),
                    name=raw,
                    matching=nameify(normalizers, quote='\'')))
        raise NameError(
            'Unknown normalizer {name}'.format(
                name=nameify([name], quote='\'')))
    raise ValueError('No normalizer specified')


def list_normalizers(index: Dict = None) -> List[str]:
    """Return a list of normalizers.

    Parameters
    ----------
    register:
        The register in which the normalizer was registered.
        If omitted, the global register will be used.

    Returns
    -------
        A list of the names for the available normalizers.
    """
    index = index if index is not None else NORMALIZERS
    return list(index.keys())
