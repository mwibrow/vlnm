"""
Helpers for tests.
"""
import itertools

import numpy as np
import pandas as pd

def make_set_up(set_up=None):
    """Make the set up function for a repeating test."""
    def _do_set_up(obj):
        if set_up:
            return set_up(obj)
        return obj.setUp()
    return _do_set_up

def repeat_test(iterations=100, seed=None, set_up=None):
    """
    Decorator for repeating tests with random numbers.
    """
    set_up = make_set_up(set_up=set_up)
    def _decorator(method):
        def _wrapper(self, *args, **kwargs):
            np.random.seed(seed)
            for _ in range(iterations):
                set_up(self)
                method(self, *args, **kwargs)
        _wrapper.__name__ = method.__name__
        return _wrapper
    return _decorator

def generate_data_frame(
        speakers=1,
        genders=None,
        factors=None,
        na_percentage=0):
    """
    Generate a random(ish) data-frame for testing.
    """
    df_factors = factors.copy()
    df_factors.update(speaker=[speaker for speaker in range(speakers)])
    base_df = pd.DataFrame(
        list(itertools.product(*df_factors.values())),
        columns=df_factors.keys())
    index = base_df['speaker'] % len(genders)
    base_df['gender'] = np.array(genders)[index]
    formants = ['f0', 'f1', 'f2', 'f3']
    for f, formant in enumerate(formants):
        base_df[formant] = (index + 1) * 250 + f * 400
        base_df[formant] += np.random.randint(50, size=len(base_df)) - 25
        i = np.random.random(len(base_df)) > (na_percentage / 100.)
        base_df.loc[i, formant] = np.nan
    return base_df
