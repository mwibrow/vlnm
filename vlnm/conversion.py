"""
Miscellaeneous conversion functions.
"""

import numpy as np

from .docstrings import docstring


@docstring
def hz_to_bark(frq):
    r"""Convert Hz to Bark scale according to :citet:`traunmuller_1990`.

    .. math::

        f^\prime = 26.81 \left(\frac{f}{f + 1960}\right)

    {{hz_to_bark}}
    """
    return hz_to_bark_traunmuller(frq)

def hz_to_bark_zwicker(frq):
    r"""Convert Hz to Bark scale according to :citet:`zwicker_terhardt_1980`.

    .. math::

        f^\prime = 13 \arctan\left( 0.76\frac{f}{1000} \right) +
         3.5 \arctan \left( \frac{f}{7500} \right)^2


    """
    return (13 * np.arctan(0.00076 * frq) +
            3.5 * np.arctan(frq / 7500.) ** 2)

def hz_to_bark_greenwood(frq):
    return 11.9 * np.log10(frq / 165.4 + 0.88)

def hz_to_bark_volk(frq):
    r"""Convert Hz to Bark scale according to :citet:`volk_2015`.

    .. math::

        f^\prime  = 32.12 \left(
            1 - \left(1 +
                \left(\frac{f}{873.47}\right)^{1.18}
            \right)^{-0.4}
        \right)


    """

    return 32.12 * (1. - (1. + (frq / 873.47) ** 1.18) ** -0.4)

def hz_to_bark_traunmuller(frq):
    return 26.81 * frq / (frq + 1960) - 0.53

def hz_to_mel(frq):
    r"""
    Convert Hz to mel scale.

    .. math::

       M = 1127\log\left(1 + \frac{f}{700}\right)

    """
    return 1127. * np.log(1. + frq / 700.)


def hz_to_erb(frq):
    r"""
    Convert Hz to approximate ERB scale.

    .. math::

       E = 21.4\log\left(1 + 0.00437f\right)

    """
    return 21.4 * np.log(1 + 0.00437 * frq)
