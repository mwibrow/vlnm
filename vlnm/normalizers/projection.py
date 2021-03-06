"""
Projection normalizers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains normalizers which can be
used to perform supervised or unsupervised dimensionality reduction
on vowel formant data,
for example, projecting
:math:`F_0`, :math:`F_1`, :math:`F_2`, :math:`F_3`
data (i.e., four-dimensional data)
onto two dimensions.


.. normalizers-list::
    :module: vlnm.normalizers.projection

"""

from typing import List, Union, Type
import pandas as pd
from sklearn.decomposition import FactorAnalysis, FastICA, PCA, NMF
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

from ..docstrings import docstring
from .base import (
    register,
    classify,
    FormantGenericNormalizer,
    uninstantiable)


@uninstantiable
class SupervisedProjectionNormalizer(FormantGenericNormalizer):
    """Base class for supervised dimension reduction Normalizers."""

    def __init__(
            self,
            cls: Type,
            vowel: str = 'vowel',
            columns: List[str] = None,
            rename: Union[str, List[str]] = None,
            groupby: Union[str, List[str]] = None,
            n_components: int = None,
            **kwargs):
        super().__init__(formants=[vowel] + (columns or []), rename=rename, groupby=groupby)
        self.vowel = vowel
        self.estimator = cls(n_components=n_components, **kwargs)
        self.n_components = n_components

    def _norm(self, df: pd.DataFrame, **kwargs):
        columns = self.params['formants'][1:]  # NB not necessarily formants.
        data = df[columns].values
        labels = df[self.vowel].astype('category').cat.codes
        fit = self.estimator.fit_transform(data, labels)
        df.drop(columns, axis=1)
        new_columns = self._get_outputs()
        df[new_columns] = fit[:, :self.n_components]
        return df

    def _get_outputs(self):
        return ['f{}'.format(i + 1) for i in range(self.n_components)]


@uninstantiable
class UnsupervisedProjectionNormalizer(FormantGenericNormalizer):
    """Base class for unsupervised dimension reduction Normalizers."""

    def __init__(
            self,
            cls: Type,
            columns: List[str] = None,
            rename: Union[str, List[str]] = None,
            groupby: Union[str, List[str]] = None,
            n_components: int = None,
            **kwargs):
        super().__init__(formants=columns, rename=rename, groupby=groupby)
        self.estimator = cls(n_components=n_components, **kwargs)
        self.n_components = n_components

    def _norm(self, df: pd.DataFrame, **kwargs):
        columns = self.params['formants']  # NB not necessarily formants.
        data = df[columns].values
        fit = self.estimator.fit_transform(data)
        df.drop(columns, axis=1)
        new_columns = self._get_outputs()
        df[new_columns] = fit[:, :self.n_components]
        return df

    def _get_outputs(self):
        return ['f{}'.format(i + 1) for i in range(self.n_components)]


@docstring
@register('lda')
@classify(vowel='extrinsic', formant='extrinsic', speaker='extrinsic')
class LDANormalizer(SupervisedProjectionNormalizer):
    r"""Normalize data using Linear Discriminant Analysis (LDA).

    See :citet:`wang_van-heuven_2006` for an example of applying
    LDA to phonetic data.

    Parameters
    ----------
    vowel:
    columns:
        The columns of the |dataframe| which contain the
        features to use in LDA.
        This does not have to be formant data, but *must*
        be numeric.
    n_components:
        The required number of components.
        Should be equal to or less than the number of columns
        specified.


    Other parameters
    ----------------
    rename:
    groupby:
    \*\*kwargs:
        All other paremeters are passed to the
        constructor of the :class:`sklearn.discriminant_analysis.LinearDiscriminantAnalysis`
        class.


    Examples
    --------

    .. ipython::

        from vlnm import pb1952, LDANormalizer

        df = pb1952(['speaker', 'vowel', 'f0', 'f1', 'f2', 'f3'])
        norm = LDANormalizer(
            vowel='vowel',
            columns=['f0', 'f1', 'f2', 'f3'],
            n_components=2,
            rename='{}*')
        norm_df = norm.normalize(df)
        norm_df.head()


    """

    def __init__(
            self,
            vowel: str = 'vowel',
            columns: List[str] = None,
            n_components: int = 2,
            rename: Union[str, dict] = None,
            groupby: Union[str, List[str]] = None,
            **kwargs):
        super().__init__(
            LinearDiscriminantAnalysis,
            vowel=vowel,
            columns=columns,
            rename=rename,
            n_components=n_components,
            **kwargs)

    @docstring
    def normalize(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        return super().normalize(df, **kwargs)


@docstring
@register('factor-analysis')
@classify(vowel='extrinsic', formant='extrinsic', speaker='extrinsic')
class FactorAnalysisNormalizer(UnsupervisedProjectionNormalizer):
    r"""Normalize data using Factor Analayis (FA).

    Parameters
    ----------
    columns:
        The columns of the |dataframe| which contain the
        features to use in FA.
        This does not have to be formant data, but *must*
        be numeric.
    n_components:
        The required number of components.
        Should be equal to or less than the number of columns
        specified.


    Other parameters
    ----------------
    rename:
    groupby:
    \*\*kwargs:
        All other paremeters are passed to the
        constructor of the :class:`sklearn.decomposition.FactorAnalysis`
        class.


    Examples
    --------

    .. ipython::

        from vlnm import pb1952, FactorAnalysisNormalizer

        df = pb1952(['speaker', 'vowel', 'f0', 'f1', 'f2', 'f3'])
        norm = FactorAnalysisNormalizer(
            columns=['f0', 'f1', 'f2', 'f3'],
            n_components=2,
            rename='{}*')
        norm_df = norm.normalize(df)
        norm_df.head()


    """

    def __init__(
            self,
            columns: List[str] = None,
            n_components: int = 2,
            rename: Union[str, dict] = None,
            groupby: Union[str, List[str]] = None,
            **kwargs):
        super().__init__(
            FactorAnalysis,
            columns=columns,
            rename=rename,
            n_components=n_components,
            **kwargs)

    @docstring
    def normalize(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        return super().normalize(df, **kwargs)


@docstring
@register('fast-ica')
@classify(vowel='extrinsic', formant='extrinsic', speaker='extrinsic')
class FastICANormalizer(UnsupervisedProjectionNormalizer):
    r"""Normalize data using (fast) Independent Components Analysis (ICA).

    Parameters
    ----------
    columns:
        The columns of the |dataframe| which contain the
        features to use in ICA.
        This does not have to be formant data, but *must*
        be numeric.
    n_components:
        The required number of components.
        Should be equal to or less than the number of columns
        specified.


    Other parameters
    ----------------
    rename:
    groupby:
    \*\*kwargs:
        All other paremeters are passed to the
        constructor of the :class:`sklearn.decomposition.FastICA`
        class.


    Examples
    --------

    .. ipython::

        from vlnm import pb1952, FastICANormalizer

        df = pb1952(['speaker', 'vowel', 'f0', 'f1', 'f2', 'f3'])
        norm = FastICANormalizer(
            columns=['f0', 'f1', 'f2', 'f3'],
            n_components=2,
            rename='{}*')
        norm_df = norm.normalize(df)
        norm_df.head()


    """

    def __init__(
            self,
            columns: List[str] = None,
            n_components: int = 2,
            rename: Union[str, dict] = None,
            groupby: Union[str, List[str]] = None,
            **kwargs):
        super().__init__(
            FastICA,
            columns=columns,
            rename=rename,
            n_components=n_components,
            **kwargs)

    @docstring
    def normalize(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        return super().normalize(df, **kwargs)


@docstring
@register('pca')
@classify(vowel='extrinsic', formant='extrinsic', speaker='extrinsic')
class PCANormalizer(UnsupervisedProjectionNormalizer):
    r"""Normalize data using Principle Components Analysis (PCA).

    See :citet:`jacobi_etal_2006` for an example of applying
    PCA to phonetic data.

    Parameters
    ----------
    columns:
        The columns of the |dataframe| which contain the
        features to use in PCA.
        This does not have to be formant data, but *must*
        be numeric.
    n_components:
        The required number of components.
        Should be equal to or less than the number of columns
        specified.


    Other parameters
    ----------------
    rename:
    groupby:
    \*\*kwargs:
        All other paremeters are passed to the
        constructor of the :class:`sklearn.decomposition.PCA`
        class.


    Examples
    --------

    .. ipython::

        from vlnm import pb1952, PCANormalizer

        df = pb1952(['speaker', 'vowel', 'f0', 'f1', 'f2', 'f3'])
        norm = PCANormalizer(
            columns=['f0', 'f1', 'f2', 'f3'],
            n_components=2,
            rename='pc')
        norm_df = norm.normalize(df)
        norm_df.head()


    """

    def __init__(
            self,
            columns: List[str] = None,
            n_components: int = 2,
            rename: Union[str, dict] = None,
            groupby: Union[str, List[str]] = None,
            **kwargs):
        super().__init__(
            PCA,
            columns=columns,
            rename=rename,
            n_components=n_components,
            **kwargs)

    @docstring
    def normalize(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        return super().normalize(df, **kwargs)


@docstring
@register('nmf')
@classify(vowel='extrinsic', formant='extrinsic', speaker='extrinsic')
class NMFNormalizer(UnsupervisedProjectionNormalizer):
    r"""
    Normalize data using Non-negative Matrix Factorization (NMF).

    Parameters
    ----------
    columns:
        The columns of the |dataframe| which contain the
        features to use in NMF.
        This does not have to be formant data, but *must*
        be numeric.
    n_components:
        The required number of components.
        Should be equal to or less than the number of columns
        specified.


    Other parameters
    ----------------
    rename:
    groupby:
    \*\*kwargs:
        All other paremeters are passed to the
        constructor of the :class:`sklearn.decomposition.NMF`
        class.


    Examples
    --------

    .. ipython::

        from vlnm import pb1952, NMFNormalizer

        df = pb1952(['speaker', 'vowel', 'f0', 'f1', 'f2', 'f3'])
        norm = NMFNormalizer(
            columns=['f0', 'f1', 'f2', 'f3'],
            n_components=2,
            rename='{}*')
        norm_df = norm.normalize(df)
        norm_df.head()

    """

    def __init__(
            self,
            columns: List[str] = None,
            n_components: int = 2,
            rename: Union[str, dict] = None,
            groupby: Union[str, List[str]] = None,
            **kwargs):
        super().__init__(
            NMF, columns=columns, rename=rename, n_components=n_components, **kwargs)

    @docstring
    def normalize(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        return super().normalize(df, **kwargs)
