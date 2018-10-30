"""
    Normalizers package.
    ~~~~~~~~~~~~~~~~~~~~

    .. autofunction:: normalize
"""
from vlnm.utils import nameify

NORMALIZERS = {}

def register_normalizer(cls, *aliases, register=None):
    """Register a normalizer to be used with the normalize function."""
    register = NORMALIZERS if register is None else register
    for alias in aliases:
        register[alias] = cls

def get_normalizer(method):
    """Return a normalizer."""
    raw = method
    method = method.lower()
    if method:
        normalizers = [name for name in NORMALIZERS
                       if name.lower().startswith(method)]
        if normalizers:
            if len(normalizers) == 1:
                return NORMALIZERS[normalizers[0]]
            raise NameError(
                'Found {count} normalizers matching {name}:'
                '{matching}'.format(
                    count=len(normalizers),
                    name=raw,
                    matching=nameify(normalizers, quote='\'')))
        raise NameError(
            'Unknown normalizer {name}'.format(
                name=nameify([method], quote='\'')))
    raise NameError('No normalizer specified')

def list_normalizers():
    """Return a list of normalizers."""
    return list(NORMALIZERS.keys())
