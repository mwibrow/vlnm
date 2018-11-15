"""
Miscellaeneous conversion functions.
"""

import numpy as np

from .docstrings import docstring


@docstring
def hz_to_bark(frq, method='traunmuller'):
    r"""Convert Hz to Bark scale according to

    Parameters
    ----------

    frq : :obj:`numpy.ndarray` | :obj:`pandas.DataFrame`
        The frequency data to convert.

    method : :obj:`str`
        The conversion method used, from the list below.
        If not given, defaults to ``'traumuller'``.

        - ``'syrdal'`` conversion from :citet:`syrdal_gopal_1986`.

            .. math::

                F^\prime = 13 \arctan\left( 0.76\frac{F_c}{1000} \right) +
                    3.5 \arctan \left( \frac{F_c}{7500} \right)^2

            where

            .. math::

                F_c = \begin{cases}
                    150 & \mbox{when } F < 150
                    \\
                    F - 0.2(F - 150) & \mbox{when } 150 \leq F < 200
                    \\
                    F - 0.2(250 - F) & \mbox{when } 200\leq F < 250
                    \\
                    F & \mbox{otherwise}
                    \end{cases}

        - ``'traumuller'`` conversion from :citet:`traunmuller_1990`.

        .. math::

            F^\prime = 26.81 \left(\frac{F}{F + 1960}\right)

        - ``'volk'`` conversion from :citet:`volk_2015`.

        .. math::

            F^\prime  = 32.12 \left(
                1 - \left(1 +
                    \left(\frac{F}{873.47}\right)^{1.18}
                \right)^{-0.4}
            \right)

        - ``'zwicker'`` conversion from :citet:`zwicker_terhardt_1980`.

        .. math::

            F^\prime = 13 \arctan\left( 0.76\frac{F}{1000} \right) +
            3.5 \arctan \left( \frac{F}{7500} \right)^2

    Return
    ------
    :obj:`numpy.ndarray` | :obj:`pandas.DataFrame`
        The converted data.
    """
    if method == 'greenwood':
        return 11.9 * np.log10(frq / 165.4 + 0.88)
    elif method == 'syrdal':
        frq[frq < 150.] = 150.
        frq[(frq >= 150.) & (frq < 200)] = frq - (0.2 * (frq - 150.))
        frq[(frq >= 200.) & (frq < 250)] = frq - (0.2 * (250. - frq))
        return hz_to_bark(frq, method='zwicker')
    elif method == 'traunmuller':
        return 26.81 * frq / (frq + 1960) - 0.53
    elif method == 'volk':
        return 32.12 * (1. - (1. + (frq / 873.47) ** 1.18) ** -0.4)
    elif method == 'zwicker':
        return (13 * np.arctan(0.00076 * frq) +
                3.5 * np.arctan(frq / 7500.) ** 2)
    raise ValueError('Unknown method: {}'.format(method))


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
