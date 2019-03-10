"""
Speaker-based normalizers
~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from typing import List, Union

import numpy as np
import pandas as pd

from ..docstrings import docstring
from .base import register, classify
from .base import Normalizer, FormantsNormalizer, FxNormalizer


class SpeakerNormalizer(Normalizer):
    """Base class for speaker intrinsic normalizers."""

    config = dict(
        columns=['speaker']
    )

    def _normalize(self, df):
        speaker = self.options.get('speaker') or 'speaker'
        return df.groupby(by=speaker, as_index=False).apply(
            super()._normalize)


@docstring
@register('gerstman')
@classify(vowel='extrinsic', formant='intrinsic', speaker='intrinsic')
class GerstmanNormalizer(SpeakerNormalizer, FormantsNormalizer):
    r"""Normalize formants according to :citet:`gerstman_1968`.

    Formants are normalized by subtracting the speaker's minimum value
    for the formant and then divided by the speaker's range for
    the formant. These value are then multipled by :math:`999`.

    .. math::

        F_i^\prime = 999 \frac{F_i - \min{F_i}}{\max{F_i}}

    Parameters
    ----------
    {% formants %}
    {% speaker %}
    {% rename %}
    """

    def __init__(
            self,
            formants: List[str] = None,
            speaker: str = 'speaker',
            rename: str = None, **kwargs):
        super().__init__(speaker=speaker, formants=formants, rename=rename, **kwargs)

    @docstring
    def normalize(
            self,
            df,
            formants: List[str] = None,
            rename: str = None,
            **kwargs):
        """{% normalize %}"""
        return super().normalize(
            df,
            formants=formants,
            rename=rename, **kwargs)

    def _norm(self, df):
        formants = self.params['formants']
        fmin = df[formants].min(axis=0)
        fmax = df[formants].max(axis=0)
        df[formants] = 999 * (df[formants] - fmin) / (fmax - fmin)
        return df


@docstring
@register('lce')
@classify(vowel='extrinsic', formant='intrinsic', speaker='intrinsic')
class LCENormalizer(SpeakerNormalizer, FormantsNormalizer):
    r"""Normalize by dividing formants by their mamximum value for a speaker.

    Formants are normalized by "linear compression or expansion"
    :citep:`{% lobanov_1971 %} p.607`, that is by dividing
    each formant for a given speaker by it's maximum value for that speaker:

    .. math::

        F_i^\prime = \frac{F_i}{\max{F_i}}

    Parameters
    ----------
    {% speaker %}
    {% formants %}
    {% rename %}
    """

    def __init__(
            self, speaker: str = 'speaker', formants: List[str] = None,
            rename: str = None, **kwargs):
        super().__init__(speaker=speaker, formants=formants, rename=rename, **kwargs)

    @docstring
    def normalize(
            self, df: pd.DataFrame, speaker: str = 'speaker',
            formants: List[str] = None, rename: str = None,
            **kwargs) -> pd.DataFrame:
        """{% normalize %}"""
        return super().normalize(
            df, speaker=speaker, formants=formants, rename=rename, **kwargs)

    def _norm(self, df):
        formants = self.params['formants']
        df[formants] = df[formants] / df[formants].max(axis=0)
        return df


@docstring
@register('lobanov')
@classify(vowel='extrinsic', formant='intrinsic', speaker='intrinsic')
class LobanovNormalizer(SpeakerNormalizer, FormantsNormalizer):
    r"""Normalize formants using their z-score for a given speaker.

    This uses the formula given in :citet:`{% lobanov_1971 %} p.607`:

    .. math::

        F_i^\prime = \frac{F_i - \mu_{F_i}}{\sigma_{F_i}}

    Where :math:`\mu_{F_i}` and :math:`\sigma_{F_i}` are the
    mean and standard deviation (respectively) of the
    formant :math:`F_i` for a given speaker.

    Parameters
    ----------
    {% formants %}
    {% rename %}
    """

    def __init__(
            self, speaker: str = 'speaker', formants: List[str] = None,
            rename: str = None, **kwargs):
        super().__init__(speaker=speaker, formants=formants, rename=rename, **kwargs)

    @docstring
    def normalize(self, df: pd.DataFrame, formants: List[str] = None,
                  rename: str = None, **kwargs) -> pd.DataFrame:
        """{% normalize %}"""
        return super().normalize(df, formants=formants, rename=rename, **kwargs)

    def _norm(self, df):
        formants = self.params['formants']
        mean = df[formants].mean(axis=0)
        std = df[formants].std(axis=0)
        df[formants] = (df[formants] - mean) / std
        return df


@docstring
@register('neary')
@classify(vowel='extrinsic', formant='intrinsic', speaker='intrinsic')
class NearyNormalizer(SpeakerNormalizer, FormantsNormalizer):
    r"""Normalize by subtracting log-transformed formant means for each speaker.

    .. math::

        F_i^\prime = T\left(
            \log\left(F_i\right) - \frac{1}{n}
                \sum_{j=1}^{n}\mu_{\log\left(F_j\right)}
        \right)

    Where :math:`T(x)=x` or :math:`T(x)=\exp(x)`,
    and `n` is the highest formant index.

    Parameters
    ----------

    {% formants %}
    {% speaker %}
    exp:
        If :obj:`True` transform the normalized formants
        using the exponential function with base :math:`e`.
    {% rename %}

    """
    config = dict(
        columns=['speaker', 'f1', 'f2', 'f3'],
        keywords=['speaker', 'exp']
    )

    def __init__(
            self,
            formants: List[str] = None,
            exp: bool = False,
            rename: str = None,
            **kwargs):
        super().__init__(formants=formants, exp=exp, rename=rename, **kwargs)

    @docstring
    def normalize(
            self,
            df: pd.DataFrame,
            formants: List[str] = None,
            exp: bool = False,
            rename: str = None, **kwargs):
        """{% normalize %}"""
        return super().normalize(
            df, formants=formants, exp=exp, rename=rename, **kwargs)

    def _keyword_default(self, keyword, df=None):
        if keyword == 'exp':
            return False
        return super()._keyword_default(keyword, df=df)

    def _norm(self, df):
        formants = self.params['formants']
        logs = np.log(df[formants])
        df[formants] = np.log(df[formants]) - logs.mean(axis=0)
        if self.params['exp']:
            df[formants] = np.exp(df[formants])
        return df


@docstring
@register('nearygm')
@classify(vowel='extrinsic', formant='extrinsic', speaker='intrinsic')
class NearyGMNormalizer(SpeakerNormalizer, FxNormalizer):
    r"""Normalize by subtracting the speaker's mean log-transformed formants.

    The Neary 'Grand Mean' normalizer log-transforms each formant
    and then substracts the mean log-transform of *all* formants
    under-considraton for a given speaker.
    This may be |f1| and |f2| :citep:`flynn_foulkes_2011`
    or |f1|, |f2|, and |f3| :citep:`clopper_2009`:

    .. math::

        F_i^\prime = T\left(
            \log\left(F_i\right) - \frac{1}{n}
                \sum_{j=1}^{n}\mu_{\log\left(F_j\right)}
        \right)

    Where :math:`T(x)=x` or :math:`T(x)=\exp(x)`,
    and `n` is the highest formant index.

    Parameters
    ----------
    {% f1 %}
    {% f2 %}
    {% f3 %}
    {% formants %}
    {% speaker %}
    exp:
        If :obj:`True` transform the normalized formants
        using the exponential function with base :math:`e`.
    {% rename %}

    """

    config = dict(
        columns=['speaker', 'f1', 'f2', 'f3'],
        keywords=['speaker', 'exp']
    )

    def __init__(
            self,
            f1: Union[str, List[str]] = None,
            f2: Union[str, List[str]] = None,
            f3: Union[str, List[str]] = None,
            speaker: str = None,
            exp: bool = False,
            rename: str = None):
        super().__init__(
            f1=f1, f2=f2, f3=f3,
            speaker=speaker, exp=exp, rename=rename)

    @docstring
    def normalize(
            self,
            df: pd.DataFrame,
            f1: Union[str, List[str]] = None,
            f2: Union[str, List[str]] = None,
            f3: Union[str, List[str]] = None,
            formants: List[str] = None,
            speaker: str = None,
            exp: bool = False,
            rename: str = None,
            **kwargs):
        """{% normalize %}"""
        return super().normalize(
            df, f1=f1, f2=f2, f3=f3, formants=formants,
            speaker=speaker, exp=exp, rename=rename, **kwargs)

    def _keyword_default(self, keyword, df=None):
        if keyword == 'exp':
            return False
        return super()._keyword_default(keyword, df=df)

    def _norm(self, df):
        formants = self.params['formants']
        logs = np.log(df[formants])
        df[formants] = logs - logs.mean(axis=0).mean()
        if self.params['exp']:
            df[formants] = np.exp(df[formants])
        return df
