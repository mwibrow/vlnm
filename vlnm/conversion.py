"""
Conversion
~~~~~~~~~~

This module contains miscellaeneous functions for converting
from Hz to other scales.
"""

import numpy as np
import pandas as pd


def hz_to_bark(frq: np.ndarray, method: str = 'traunmuller') -> np.ndarray:
    r"""Convert from Hz to Bark scale.

    Parameters
    ----------

    frq :
        The frequency data to convert.

    method :
        The conversion method used, from the list below.
        If not given, defaults to ``'traumuller'``.

        - ``'syrdal'`` conversion from :citet:`syrdal_gopal_1986`:

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

        - ``'traumuller'`` conversion from :citet:`traunmuller_1990`:

        .. math::

            F^\prime = 26.81 \left(\frac{F}{F + 1960}\right)

        - ``'volk'`` conversion from :citet:`volk_2015`:

        .. math::

            F^\prime  = 32.12 \left(
                1 - \left(1 +
                    \left(\frac{F}{873.47}\right)^{1.18}
                \right)^{-0.4}
            \right)

        - ``'zwicker'`` conversion from :citet:`zwicker_terhardt_1980`:

        .. math::

            F^\prime = 13 \arctan\left( 0.76\frac{F}{1000} \right) +
            3.5 \arctan \left( \frac{F}{7500} \right)^2

    Return
    ------
    :
        The converted data.
    """
    if not isinstance(frq, pd.DataFrame):
        frq = np.atleast_1d(frq)
    if method == 'greenwood':
        return 11.9 * np.log10(frq / 165.4 + 0.88)
    if method == 'syrdal':
        frq[frq < 150.] = 150.
        frq[(frq >= 150.) & (frq < 200)] = frq - (0.2 * (frq - 150.))
        frq[(frq >= 200.) & (frq < 250)] = frq - (0.2 * (250. - frq))
        return hz_to_bark(frq, method='zwicker')
    if method == 'traunmuller':
        return 26.81 * frq / (frq + 1960) - 0.53
    if method == 'volk':
        return 32.12 * (1. - (1. + (frq / 873.47) ** 1.18) ** -0.4)
    if method == 'zwicker':
        return (13 * np.arctan(0.00076 * frq) +
                3.5 * np.arctan(frq / 7500.) ** 2)
    raise ValueError('Unknown method: {}'.format(method))


def hz_to_mel(frq: np.ndarray) -> np.ndarray:
    r"""Convert from Hz to mel scale.

    The formula used here is the 'natural-log' equivalent
    of the formula given in :citet:`{% oshaughnessy_1987 %}, p.150`:

    .. math::

       F^\prime = 1127\log\left(1 + \frac{F}{700}\right)

    Parameters
    ----------

    frq:
        The frequency data to convert.

    Return
    ------
    :
        The converted data.
    """
    return 1127. * np.log(1. + frq / 700.)


def hz_to_erb(frq: np.ndarray) -> np.ndarray:
    r"""Convert Hz to approximate ERB scale.

    Formula taken from :citet:`{% moore_glasberg_1996 %}, p.336`:

    .. math::

       F^\prime = 21.4\log\left(1 + 0.00437F\right)

    Parameters
    ----------

    frq :
        The frequency data to convert.

    Return
    ------
    :
        The converted data.
    """
    return 21.4 * np.log(1 + 0.00437 * frq)


def hz_to_log(frq: np.ndarray) -> np.ndarray:
    r"""Convert Hz to the natural logarithmic scale.

    .. math::

       F^\prime = \log\left(F\right)

    Parameters
    ----------

    frq :
        The frequency data to convert.

    Return
    ------
    :
        The converted data.
    """
    return np.log(frq)


def hz_to_log10(frq: np.ndarray) -> np.ndarray:
    r"""Convert Hz to the base-10 logarithmic scale.

    .. math::

       F^\prime = \log_{10}\left(F\right)

    Parameters
    ----------

    frq :
        The frequency data to convert.

    Return
    ------
    :
        The converted data.
    """
    return np.log(frq)
