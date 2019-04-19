"""
The :mod:`vlnm.registration` module implements
helper functions for documenting normalizer classes
and registering them for use with the :func:`normalize` function.
"""

from typing import Dict

from .utils import nameify

NORMALIZERS = {}


def register_normalizer(klass: 'Normalizer', name: str, index: Dict = None):
    """Register a normalizer to be used with the normalize function.

    Parameters
    ----------
    klass: :class:`Normalizer`
        A normalizer class.
    name:
        Name that can be used to refer to access the class in the
        :func:`.get_normalizer` function.
    index:
        A dictionary in which the normalizer class will be registered.
        If omitted, the global index will be used.

    Returns
    -------
        A decorator function.

    Example
    -------

    .. ipython::
        run: no

        class CustomNormalizer(Normalizer):
            # Custom normalizer definition.

        register_normalizer(CustomNormalizer, 'custom-normalizer')

    """
    index = NORMALIZERS if index is None else index
    index[name] = klass


def register(name: str):
    """Decorator for registering a normalizer class.

    Parameters
    ----------
        name:
            The name to use for the class.
            Internally, the :func:`.register_normalizer`
            function is called.

    Returns
    -------
         A decorator function.

    Example
    -------

    .. ipython::
        run: no

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

    Parameters
    ----------
        vowel:
            One of ``intrinsic`` or ``extrinsic``.
        formant:
            One of ``intrinsic`` or ``extrinsic``
        speaker:
            One of ``intrinsic`` or ``extrinsic``

    Returns
    -------
        A decorator function.

    Example
    -------

    .. ipython::
        run: no
        before: from vlnm.registration import classify

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

    Example
    -------

    .. ipython::

        from vlnm.registration import get_normalizer
        nrm = get_normalizer('lobanov')
        print(nrm)

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
