"""
Miscellaeneous conversion functions.
"""

import numpy as np

def hz_to_bark(frq):
    r"""
    Convert Hz to bark scale.

    .. math::

        f^\prime = 26.81 \displayfrac{f}{f + 1960}\right)

    .. math::
        f^\prime = 13. * np.arctan()

    """
    return 26.81 * frq / (frq + 1960) - 0.53

class HzToBark:
    """Callable class for converting Hz to Bark.

    hz_to_bark['traunmuller']
    """

    def __init__(self, method: str = 'traunmuller'):
        self.method = method

    def __call__(self, frq):
        self.hz_to_bark(frq)

    def __getitem__(self, method):
        return HzToBark(method)

    def hz_to_bark(self, frq):
        """Convert from Hz to Bark.
        """
        if self.method == 'zwicker':
            return (13 * np.arctan(0.76 * frq / 1000.) +
                    3.5 * np.arctan(frq / 7500.) ** 2)
        elif self.method == 'greenwood':
            return 11.9 * np.log10(frq / 165.4 + 0.88)

        elif self.method == 'volk':
            return 32.12 * (1. - (1. + (frq / 873.47) ** 1.18) ** -0.4)

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
