"""
Miscellaeneous conversion functions.
"""

import numpy as np

def hz_to_bark(frq):
    r"""
    Convert Hz to bark scale.

    .. math::

       f^\prime = 26.81 \displayfrac{f}{f + 1960}\right)

    """
    return 26.81 * frq / (frq + 1960) - 0.53

def hz_to_mel(frq):
    r"""
    Convert Hz to mel scale.

    .. math::

       f^\prime = 1127\log\left(1 + \displayfrac{f}{700}\right)

    """
    return 1127. * np.log(1. + frq / 700.)


def hz_to_erb(frq):
    r"""
    Convert Hz to approximate ERB scale.

    .. math::

       f^\prime = 21.4\log\left(1 + 0.00437f\right)

    """
    return 21.4 * np.log(1 + 0.00437 * frq)
