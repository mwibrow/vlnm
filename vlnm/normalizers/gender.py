"""
Gender-based normalizers
~~~~~~~~~~~~~~~~~~~~~~~~

Normalizers which adjust calculations based
on the speaker's identified/identifying gender.
Note, that as defined in the literature
:citep:`e.g., {% bladon_etal_1984, nordstrom_1977 %}`
the normalizers use a binary gender classification.

.. normalizers-list::
    :module: vlnm.normalizers.gender

"""
from typing import List, Union

import numpy as np
import pandas as pd

from vlnm.conversion import hz_to_bark
from vlnm.docstrings import docstring
from .base import (
    classify,
    register,
    FormantGenericNormalizer,
    FormantSpecificNormalizer)
from .speaker import SpeakerNormalizer


@docstring
@register('bladen')
@classify(vowel='intrinsic', formant='intrinsic', speaker='intrinsic')
class BladenNormalizer(SpeakerNormalizer, FormantGenericNormalizer):
    r"""Normalize formant data according to :citet:`bladon_etal_1984`.

    For a given speaker, formants are normalized as follows:

    .. math::

        F_{i}^* = 26.81 \left(
            1 + \frac{F_i}{F_i + 1960}
            \right) - 0.53 - I(F_i)

    Where :math:`I(F_i)` is an indicator function returning 1 if
    :math:`F_i` was produced by a speaker
    identified/identifying as female, and 0 otherwise.

    Parameters
    ----------
    formants:
    gender:
        The |dataframe| column containing the gender labels.
    female:
        The label in the |dataframe| indicating a speaker
        identified/identifying as female.
        If omitted, defaults to ``F``.
    male:
        The label in the |dataframe| indicating a speaker
        identified/identifying as male.
        If omitted, defaults to ``M``.


    Other Parameters
    ----------------
    rename:
    groupby:
    kwargs:


    Examples
    --------

    .. ipython::

        from vlnm import pb1952, BladenNormalizer

        df = pb1952(['speaker', 'sex', 'vowel', 'f1', 'f2'])
        norm = BladenNormalizer(
            formants=['f1', 'f2'], gender='sex', female='f', rename='{}*')
        norm_df = norm.normalize(df)
        norm_df.head()

    """
    config = dict(
        columns=['gender'],
        keywords=['gender', 'male', 'female']
    )

    def __init__(
            self,
            formants: List[str] = None,
            gender: str = 'gender',
            female: str = 'F',
            male: str = 'M',
            rename: Union[str, dict] = None,
            groupby: Union[str, List[str]] = None,
            **kwargs):
        super().__init__(
            formants=formants,
            gender=gender, female=female, male=male, rename=rename,
            groupby=groupby, **kwargs)

    def _keyword_default(self, keyword, df=None):
        if keyword == 'female':
            return 'F'
        if keyword == 'male':
            return 'M'
        return super()._keyword_default(keyword, df=df)

    def _norm(self, df):
        gender = self.params['gender']
        formants = self.params['formants']
        female = self.params['female']
        indicator = np.repeat(
            np.atleast_2d(
                (df[gender] == female).astype(float)),
            len(formants),
            axis=0).T
        return hz_to_bark(df[formants]) - indicator

    @docstring
    def normalize(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        return super().normalize(df, **kwargs)


@docstring
@register('nordstrom')
@classify(vowel='extrinsic', formant='extrinsic', speaker='extrinsic')
class NordstromNormalizer(SpeakerNormalizer, FormantSpecificNormalizer):
    r"""
    Normalize formant data according to :citet:`nordstrom_1977`.

    .. math::

        F_i^* = F_i \times
            \begin{cases}
                \frac{
                    \mu_{F_3}^{\small{male}}
                }{
                    \mu_{F_3}^{\small{female}}
                } & \mbox{if } I(F_i) = 1
                \\
                1 & \mbox{otherwise}
            \end{cases}

    Where :math:`\mu_{F_3}` is the mean :math:`F_3` across
    all vowels where :math:`F_1` is greater than 600Hz,
    and :math:`I(F_i)` is an indicator function which
    returns 1 if :math:`F_i` is from a speaker
    identified/identifying as female, and 0 otherwise.


    Parameters
    ----------
    f0, f1, f2, f3:
    gender:
        The |dataframe| column containing the gender labels.
    female:
        The label in the |dataframe| indicating a speaker
        identified/identifying as female.
    male:
        The label in the |dataframe| indicating a speaker
        identified/identifying as male.


    Other Parameters
    ----------------
    rename:
    groupby:
    kwargs:


    Examples
    --------

    .. ipython::

        from vlnm import pb1952, NordstromNormalizer

        df = pb1952(['speaker', 'sex', 'vowel', 'f1', 'f2', 'f3'])
        norm = NordstromNormalizer(gender='sex', female='f', rename='{}*')
        norm_df = norm.normalize(df)
        # Show subset of data
        norm_df[norm_df['sex'] == 'f'].head()

    """
    config = dict(
        columns=['f1', 'f3', 'gender'],
        keywords=['male', 'female', 'gender'],
        # groups=['gender']
    )

    def __init__(
            self,
            f0: Union[str, List[str]] = None,
            f1: Union[str, List[str]] = None,
            f2: Union[str, List[str]] = None,
            f3: Union[str, List[str]] = None,
            gender: str = 'gender',
            female: str = 'F',
            male: str = 'M',
            rename: Union[str, dict] = None,
            groupby: Union[str, List[str]] = None,
            **kwargs):
        super().__init__(
            f0=f0, f1=f1, f2=f2, f3=f3,
            gender=gender, female=female, male=male, rename=rename,
            groupby=groupby, **kwargs)

    def _keyword_default(self, keyword, df=None):
        if keyword == 'female':
            return 'F'
        if keyword == 'male':
            return 'M'
        return super()._keyword_default(keyword, df=df)

    def _prenormalize(self, df):
        return self.get_f3_means(df)

    def get_f3_means(self, df):
        gender = self.options['gender']
        female = self.options['female']

        constants = {}
        constants['mu_female'] = df[
            (df[gender] == female) & (df['f1'] > 600)]['f3'].mean()
        constants['mu_male'] = df[
            (df[gender] != female) & (df['f1'] > 600)]['f3'].mean()
        self.options['constants'] = constants
        return df

    def _norm(self, df):
        constants = self.params['constants']
        gender = self.params['gender']
        formants = self.params['formants']
        female = self.params['female']

        mu_female, mu_male = constants['mu_female'], constants['mu_male']

        indicator = np.repeat(
            np.atleast_2d(
                (df[gender] == female).astype(float)),
            len(formants),
            axis=0).T

        mu_female, mu_male = constants['mu_female'], constants['mu_male']
        df[formants] = (
            df[formants] * (
                1. + indicator * (mu_male / mu_female - 1.)))
        return df

    @docstring
    def normalize(
            self,
            df: pd.DataFrame,
            **kwargs) -> pd.DataFrame:
        return super().normalize(df, **kwargs)
