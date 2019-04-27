"""
Speaker-based normalizers
~~~~~~~~~~~~~~~~~~~~~~~~~


.. normalizers-list::
    :module: vlnm.normalizers.speaker

"""
from typing import List, Union

import numpy as np
import pandas as pd

from ..docstrings import docstring
from .base import register, classify
from .base import uninstantiable, Normalizer, FormantGenericNormalizer, FormantSpecificNormalizer


@uninstantiable
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
class GerstmanNormalizer(SpeakerNormalizer, FormantGenericNormalizer):
    r"""Normalize formants according to :citet:`gerstman_1968`.

    Formants are normalized by subtracting the speaker's minimum value
    for the formant and then divided by the speaker's range for
    the formant. These value are then multipled by :math:`999`.

    .. math::

        F_i^* = 999 \frac{F_i - \min{F_i}}{\max{F_i}}

    Parameters
    ----------

    formants:
    speaker:


    Other Parameters
    ----------------
    rename:
    groupby:
    kwargs:


    Example
    -------

    .. ipython::

        import pandas as pd
        from vlnm import GerstmanNormalizer

        normalizer = GerstmanNormalizer(rename='{}*')
        df = pd.read_csv('vowels.csv')
        norm_df = normalizer.normalize(df)
        norm_df.head()
    """

    def __init__(
            self,
            formants: List[str] = None,
            speaker: str = 'speaker',
            rename: Union[str, dict] = None,
            groupby: Union[str, List[str]] = None,
            **kwargs):
        super().__init__(
            speaker=speaker,
            formants=formants,
            rename=rename,
            groupby=groupby,
            **kwargs)

    @docstring
    def normalize(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        return super().normalize(df)

    def _norm(self, df):
        formants = self.params['formants']
        fmin = df[formants].min(axis=0)
        fmax = df[formants].max(axis=0)
        df[formants] = 999 * (df[formants] - fmin) / (fmax - fmin)
        return df


@docstring
@register('lce')
@classify(vowel='extrinsic', formant='intrinsic', speaker='intrinsic')
class LCENormalizer(SpeakerNormalizer, FormantGenericNormalizer):
    r"""Normalize by dividing formants by their mamximum value for a speaker.

    Formants are normalized by "linear compression or expansion"
    :citep:`{% lobanov_1971 %} p.607`, that is by dividing
    each formant for a given speaker by it's maximum value for that speaker:

    .. math::

        F_i^* = \frac{F_i}{\max{F_i}}

    Parameters
    ----------

    formants:
    speaker:


    Other Parameters
    ----------------
    rename:
    groupby:
    kwargs:


    Example
    -------

    .. ipython::

        import pandas as pd
        from vlnm import LCENormalizer

        normalizer = LCENormalizer(rename='{}*')
        df = pd.read_csv('vowels.csv')
        norm_df = normalizer.normalize(df)
        norm_df.head()

    """

    def __init__(
            self, speaker: str = 'speaker', formants: List[str] = None,
            rename: Union[str, dict] = None,
            groupby: Union[str, List[str]] = None,
            **kwargs):
        super().__init__(
            speaker=speaker,
            formants=formants,
            rename=rename,
            groupby=groupby,
            **kwargs)

    @docstring
    def normalize(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        return super().normalize(df)

    def _norm(self, df):
        formants = self.params['formants']
        df[formants] = df[formants] / df[formants].max(axis=0)
        return df


@docstring
@register('lobanov')
@classify(vowel='extrinsic', formant='intrinsic', speaker='intrinsic')
class LobanovNormalizer(SpeakerNormalizer, FormantGenericNormalizer):
    r"""Normalize formants using their z-score for a given speaker.

    This uses the formula given in :citet:`{% lobanov_1971 %}`:

    .. math::

        F_i^* = \frac{F_i - \mu_{F_i}}{\sigma_{F_i}}

    Where :math:`\mu_{F_i}` is the mean of the formant :math:`F_i`
    and :math:`\sigma_{F_i}` is the 'rms deviation' (:citealp:`lobanov_1971`, p.606)
    of formant :math:`F_i` from its mean for the speaker's vowels.
    As noted by :citet:`thomas_kendel_2007` this is equivalent
    to the standard deviation when the mean is zero.

    Parameters
    ----------

    formants:
    speaker:


    Other Parameters
    ----------------
    rename:
    groupby:
    kwargs:


    Example
    -------

    .. ipython::

        import pandas as pd
        from vlnm import LobanovNormalizer

        normalizer = LobanovNormalizer(rename='{}*')
        df = pd.read_csv('vowels.csv')
        norm_df = normalizer.normalize(df)
        norm_df.head()

    """

    def __init__(
            self, speaker: str = 'speaker', formants: List[str] = None,
            rename: Union[str, dict] = None,
            groupby: Union[str, List[str]] = None,
            **kwargs):
        super().__init__(
            speaker=speaker,
            formants=formants,
            rename=rename,
            groupby=groupby,
            **kwargs)

    @docstring
    def normalize(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        return super().normalize(df)

    def _norm(self, df):
        formants = self.params['formants']
        mean = df[formants].mean(axis=0)
        std = df[formants].std(axis=0)
        df[formants] = (df[formants] - mean) / std
        return df


@docstring
@register('neary')
@classify(vowel='extrinsic', formant='intrinsic', speaker='intrinsic')
class NearyNormalizer(SpeakerNormalizer, FormantGenericNormalizer):
    r"""Normalize by subtracting log-transformed formant means for each speaker.

    .. math::

        F_i^* = T\left(
            \log\left(F_i\right) - \frac{1}{n}
                \sum_{j=1}^{n}\mu_{\log\left(F_j\right)}
        \right)

    Where :math:`T(x)=x` or :math:`T(x)=\exp(x)`,
    and `n` is the highest formant index.

    Parameters
    ----------

    formants:
    speaker:
    exp:
        If :obj:`True` transform the normalized formants
        using the exponential function with base :math:`e`.


    Other Parameters
    ----------------
    rename:
    groupby:
    kwargs:


    Example
    -------

    .. ipython::

        import pandas as pd
        from vlnm import NearyNormalizer

        normalizer = NearyNormalizer(rename='{}*')
        df = pd.read_csv('vowels.csv')
        norm_df = normalizer.normalize(df)
        norm_df.head()

    """
    config = dict(
        columns=['speaker'],
        keywords=['speaker', 'exp']
    )

    def __init__(
            self,
            formants: List[str] = None,
            exp: bool = False,
            rename: Union[str, dict] = None,
            groupby: Union[str, List[str]] = None,
            **kwargs):
        super().__init__(formants=formants, exp=exp, rename=rename, groupby=groupby, **kwargs)

    @docstring
    def normalize(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        return super().normalize(df)

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
@register('neary-exp')
@classify(vowel='extrinsic', formant='intrinsic', speaker='intrinsic')
class NearyExpNormalizer(NearyNormalizer):
    r""":class:`NearyNormalizer` with the ``exp`` parameter automatically set to ``True``.

    See :cite:`thomas_kendel_2007` for discussion.

    Parameters
    ----------

    formants:
    speaker:


    Other Parameters
    ----------------
    rename:
    groupby:
    kwargs:


    Examples
    --------

    .. ipython::

        import pandas as pd
        from vlnm import NearyExpNormalizer

        normalizer = NearyExpNormalizer(rename='{}*')
        df = pd.read_csv('vowels.csv')
        norm_df = normalizer.normalize(df)
        norm_df.head()

    """

    def __init__(
            self,
            formants: List[str] = None,
            speaker: str = 'speaker',
            rename: Union[str, dict] = None,
            groupby: Union[str, List[str]] = None,
            **kwargs):
        super().__init__(formants=formants, speaker=speaker, exp=True,
                         rename=rename, groupby=groupby, **kwargs)

    @docstring
    def normalize(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        return super().normalize(df)


@docstring
@register('nearygm')
@classify(vowel='extrinsic', formant='extrinsic', speaker='intrinsic')
class NearyGMNormalizer(SpeakerNormalizer, FormantSpecificNormalizer):
    r"""Normalize by subtracting the speaker's mean log-transformed formants.

    The Neary 'Grand Mean' normalizer log-transforms each formant
    and then substracts the mean log-transform of *all* formants
    under-considraton for a given speaker.
    This is usually |f1| and |f2| :citep:`flynn_foulkes_2011`
    or |f1|, |f2|, and |f3| :citep:`clopper_2009`:

    .. math::

        F_i^* = T\left(
            \log\left(F_i\right) - \frac{1}{n}
                \sum_{j=1}^{n}\mu_{\log\left(F_j\right)}
        \right)

    Where :math:`T(x)=x` or :math:`T(x)=\exp(x)`,
    and `n` is the highest formant index.

    Parameters
    ----------

    formants:
    speaker:
    exp:
        If :obj:`True` transform the normalized formants
        using the exponential function with base :math:`e`.


    Other Parameters
    ----------------
    rename:
    groupby:
    kwargs:


    Examples
    --------

    .. ipython::

        import pandas as pd
        from vlnm import NearyGMNormalizer

        normalizer = NearyGMNormalizer(rename='{}*')
        df = pd.read_csv('vowels.csv')
        norm_df = normalizer.normalize(df)
        norm_df.head()

    """

    config = dict(
        columns=['speaker'],
        keywords=['speaker', 'exp']
    )

    def __init__(
            self,
            formants: List[str] = None,
            speaker: str = 'speaker',
            exp: bool = False,
            rename: Union[str, dict] = None,
            groupby: Union[str, List[str]] = None,
            **kwargs):
        super().__init__(
            formants=formants,
            speaker=speaker,
            exp=exp,
            rename=rename,
            groupby=groupby,
            **kwargs)

    @docstring
    def normalize(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        return super().normalize(df)

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


@docstring
@register('nearygm-exp')
@classify(vowel='extrinsic', formant='extrinsic', speaker='intrinsic')
class NearyGMExpNormalizer(NearyNormalizer):
    r""":class:`NearyGMNormalizer` with the ``exp`` parameter automatically set to ``True``.

    See :citet:`flynn_foulkes_2011` and :citet:`thomas_kendel_2007` for discussion.

    Parameters
    ----------

    formants:
    speaker:


    Other Parameters
    ----------------
    rename:
    groupby:
    kwargs:


    Example
    -------

    .. ipython::

        import pandas as pd
        from vlnm import NearyGMExpNormalizer

        normalizer = NearyGMExpNormalizer(rename='{}*')
        df = pd.read_csv('vowels.csv')
        norm_df = normalizer.normalize(df)
        norm_df.head()

    """

    def __init__(
            self,
            formants: List[str] = None,
            speaker: str = 'speaker',
            rename: Union[str, dict] = None,
            groupby: Union[str, List[str]] = None,
            **kwargs):
        super().__init__(
            formants=formants,
            speaker=speaker,
            exp=True,
            rename=rename,
            groupby=groupby,
            **kwargs)

    @docstring
    def normalize(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        return super().normalize(df)
