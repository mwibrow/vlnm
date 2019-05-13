"""
    Normalizers package.
    ~~~~~~~~~~~~~~~~~~~~
"""

import importlib
from inspect import getmembers, isclass
import os
import sys

from .base import Normalizer


WHERE_AM_I = os.path.realpath(os.path.dirname(__file__))
MODULE = sys.modules[__name__]


def _get_all():
    names = [
        name[:-3] for name in os.listdir(WHERE_AM_I)
        if name.split(os.extsep)[-1].lower() == 'py' and not name.startswith('_')]
    klasses = []
    for name in names:
        module = importlib.import_module('{}.{}'.format(__package__, name))

        klasses.extend([
            klass for klass in getmembers(module) if isclass(klass[1])
            and Normalizer in klass[1].__mro__])

    for key, value in klasses:
        setattr(MODULE, key, value)

    return sorted(list(set([klass[0] for klass in klasses])))


__all__ = _get_all()
