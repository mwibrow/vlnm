"""
Decomposition normalizers
~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains normalizers which can be
used to perform dimensionality reduction
on vowel formant data,
for example, to project
:math:`F_0`, :math:`F_1`, :math:`F_2`, :math:`F_3`
data (i.e., four-dimensional data)
onto two dimensions.


.. normalizers-list::
    :module: vlnm.normalizers.decomposition

"""

from typing import List, Union, Type
import pandas as pd
from sklearn.decomposition import PCA, NMF

from ..docstrings import docstring
from .base import (
    register,
    classify,
    FormantGenericNormalizer,
    uninstantiable)


@uninstantiable
class DecompositionNormalizer(FormantGenericNormalizer):
    """Base class for decomposition Normalizers."""

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
        new_columns = [f'f{i+1}' for i in range(fit.shape[1])]
        df[new_columns] = fit
        return df

    def _get_outputs(self):
        return ['f{}'.format(i + 1) for i in range(self.n_components)]


@docstring
@register('pca')
@classify(vowel='extrinsic', formant='extrinsic', speaker='extrinsic')
class PCANormalizer(DecompositionNormalizer):
    r"""Normalize data using Principle Components Analysis (PCA).

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
        before: |
            SetupCsv(['speaker', 'vowel', 'f0', 'f1', 'f2', 'f3])

        from vlnm import PCANormalizer

        normalizer = PCANormalizer(['f0', 'f1', 'f2', 'f3'], n_components=2, rename='{}*')
        norm_df = normalizer.normalize('vowels.csv')
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
    def normalize(self, df: Union[pd.DataFrame, str], **kwargs) -> pd.DataFrame:
        return super().normalize(df, **kwargs)


@docstring
@register('nmf')
@classify(vowel='extrinsic', formant='extrinsic', speaker='extrinsic')
class NMFNormalizer(DecompositionNormalizer):
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
    def normalize(self, df: Union[pd.DataFrame, str], **kwargs) -> pd.DataFrame:
        return super().normalize(df, **kwargs)
