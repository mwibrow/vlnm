"""
Helpers for tests.
"""

import numpy

def make_set_up(set_up=None):
    """Make the set up function for a repeating test."""
    def _do_set_up(obj):
        if set_up:
            return set_up(obj)
        else:
            return obj.setUp()
    return _do_set_up

def repeat_test(iterations=100, seed=None, set_up=None):
    """
    Decorator for repeating tests with random numbers.
    """
    set_up = make_set_up(set_up=set_up)
    def _decorator(method):
        def _wrapper(self, *args, **kwargs):
            numpy.random.seed(seed)
            for _ in range(iterations):
                set_up(self)
                method(self, *args, **kwargs)
        _wrapper.__name__ = method.__name__
        return _wrapper
    return _decorator
