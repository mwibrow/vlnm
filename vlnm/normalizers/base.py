"""
Vowel normalizer base classes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :mod:`base` module contains the base classes
for vowel normalizers as well as the
:class:`.DefaultNormalizer` which returns data unnormalized
so can be used as a control when comparing normalization methods.


.. normalizers-list::
    :module: vlnm.normalizers.base

"""

import re
from typing import Callable, List, Union

import pandas as pd

from .. import get_normalizer
from ..docstrings import docstring
from ..registration import classify, register

FORMANTS = ['f0', 'f1', 'f2', 'f3']


def uninstantiable(cls):
    def new(klass, *_, **__):
        if klass == cls:
            raise TypeError('Class "{}" cannot be instantiated'.format(cls.__name__))
        obj = object.__new__(klass)
        return obj
    cls.__new__ = new
    cls.__doc__ += '\n\n    `This class can only be instantiated by child classes`.\n'
    return cls


@docstring
@uninstantiable
class Normalizer:
    """Base normalizer class.

    The :class:`Normalizer` class forms the base of all
    normalizers and custom normalizers should all interit
    from this class or one of its subclasses.
    """

    MAX_FX = 5

    config = dict(
        # Required columns for the normalizer.
        columns=[],
        # Specifically provide the output columns.
        outputs=[],
        # Keywords used by the normalizer.
        keywords=[],
        # Default options
        options=dict())

    def __init__(self, **kwargs):
        # Class configuration.
        self.config = self._get_config()

        # Constructor options.
        self.default_options = self.config.get('options', {}).copy()
        self.default_options.update(**kwargs)

        # Did the user specify formants?
        keys = ['f{}'.format(i) for i in range(self.MAX_FX)] + ['formants']
        self.user_formants = {
            key: kwargs[key] for key in keys if kwargs.get(key)}

        # Options set up in normalize method.
        self.options = {}

        # Parameters (configuration and options) supplied to _norm method.
        self.params = {}

        self.formants = ['f{}'.format(i) for i in range(self.MAX_FX)]

    def _get_config(self):
        config = {}
        for klass in type(self).mro():
            try:
                config.update({key: value for key, value in klass.config.items()
                               if key not in config})
            except AttributeError:
                pass
        return config

    def __call__(self, df, **kwargs):
        return self.normalize(df, **kwargs)

    @staticmethod
    def _check_user_formants(df, user_formants):
        if user_formants:
            for key in user_formants:
                if isinstance(key, list):
                    for sub_key in key:
                        if not sub_key in df.columns:
                            return sub_key
                elif not key in df.columns:
                    return key
        return None

    @docstring
    def normalize(
            self, df:
            Union[pd.DataFrame, str],
            rename=None,
            groups=None,
            **kwargs) -> pd.DataFrame:

        if isinstance(df, str):
            df = pd.read_csv(df)

        self.options = self.default_options.copy()
        self.options.update(
            rename=rename or self.options.get('rename'),
            **{key: value for key, value in kwargs.items()
               if value is not None})

        self._get_formant_columns(df)

        # Check keywords.
        for keyword in self.config['keywords']:
            if not keyword in self.options:
                self.options[keyword] = self._keyword_default(keyword, df)

        # Check required columns are in the data frame.
        for column in self.config['columns']:
            column = self.options.get(column, column) or column
            try:
                if not column in df:
                    raise ValueError(
                        'Column {} not in dataframe'.format(column))
            except TypeError:
                for col in column:
                    if not col in df:
                        raise ValueError(
                            'Column {} not in dataframe'.format(col))

        self._prenormalize(df)
        groups = self.config.get('groups')
        if groups:
            norm_df = df.groupby(groups, as_index=False).apply(
                self._normalize).reset_index(drop=True)
        else:
            norm_df = self._normalize(df)
        self._postnormalize(norm_df)
        return norm_df

    def _get_formant_columns(self, df):
        formants = self.options.get('formants', self.formants) or self.formants
        try:
            formants = [
                column for column in df.columns if re.match(formants, column)]
        except TypeError:
            pass
        self.formants = formants

    def _keyword_default(self, keyword, df=None):  # pylint: disable=unused-argument
        """Get default keyword arguments."""
        return self.options.get(keyword) or keyword

    def _prenormalize(self, df):  # pylint: disable=no-self-use
        """Actions performed before normalization."""
        return df

    def _postnormalize(self, df):  # pylint: disable=no-self-use
        """Actions performed after normalization."""
        return df

    def _normalize(self, df):
        for formant_spec in self._formant_iterator():
            formant_spec['formants'] = [
                formant for formant in formant_spec['formants']
                if formant in df.columns]
            self.params = self.options.copy()
            self.params.update(**formant_spec)

            # Get the columns to subset the dataframe.
            subset = formant_spec['formants'][:]
            for column in self.config['columns']:
                if column in formant_spec:
                    subset.extend(formant_spec[column])
                else:
                    subset.append(self.params.get(column, column))

            # Throw an error if column not in dataframe or just plough on?
            subset = list(
                set(column for column in subset if column in df.columns))

            norm_df = self._norm(df[subset].copy())

            # Find new/renameable columns and rename.
            outputs = self._get_outputs()
            if outputs:
                outputs = [
                    formant_spec.get(name, self.params.get(name, name)) for name in outputs]
            else:
                outputs = [column for column in norm_df
                           if column not in subset]
                outputs.extend(self.params['formants'])
            rename = self.params.get('rename') or '{}'
            index = 1
            for column in outputs:
                if column in norm_df:
                    try:
                        new_column = rename.get(column, column)
                        if new_column is None:
                            continue
                    except AttributeError:
                        if '{}' in rename:
                            new_column = rename.format(column)
                        else:
                            new_column = '{}{}'.format(rename, index)
                            index += 1
                    df[new_column] = norm_df[column]

        return df

    def _get_outputs(self):
        return self.config.get('outputs')

    def _formant_iterator(self):
        yield dict(formants=self.formants)

    def _norm(self, df):  # pylint: disable=no-self-use
        """Implemented by subclasses"""
        return df


@docstring
@uninstantiable
class FormantSpecificNormalizer(Normalizer):
    """Base class for normalizers which require specification of individual formants.
    """

    MAX_FX = 5

    def __init__(
            self,
            f0: Union[str, List[str]] = None,
            f1: Union[str, List[str]] = None,
            f2: Union[str, List[str]] = None,
            f3: Union[str, List[str]] = None,
            f4: Union[str, List[str]] = None,
            f5: Union[str, List[str]] = None,
            **kwargs):
        super().__init__(**kwargs)

        fxs = [f0, f1, f2, f3, f4, f5]
        if any(fxs):
            formants = {
                'f{}'.format(i): fxs[i] for i in range(self.MAX_FX + 1) if fxs[i]}
        else:
            formants = dict(
                f0=f0 or 'f0',
                f1=f1 or 'f1',
                f2=f2 or 'f2',
                f3=f3 or 'f3',
                f4=f4 or 'f4',
                f5=f5 or 'f5')

        self.formants = self._sanitize_formants(formants)

    def _get_formant_columns(self, df):
        for key in self.formants.keys():
            if len(self.formants[key]) == 1:
                formant = self.formants[key][0]
                self.formants[key] = [
                    column for column in df.columns if re.match(formant, column)]
        self.formants = {key: value for key, value in self.formants.items() if value}

    def _sanitize_formants(self, formants):  # pylint: disable=no-self-use
        fxs = list(formants.keys())
        for fx in fxs:
            if not isinstance(formants[fx], list):
                if formants[fx]:
                    formants[fx] = [formants[fx]]
        return formants

    def _formant_iterator(self):
        fxs = sorted(list(self.formants.keys()))
        for formants in zip(*(self.formants[fx] for fx in fxs if fx in fxs)):
            formant_spec = {fx: formants[i] for i, fx in enumerate(formants)}
            formant_spec['formants'] = sorted(list(formant_spec.keys()))
            yield formant_spec


@docstring
@uninstantiable
class FormantGenericNormalizer(Normalizer):
    """Base class for normalizers which require general list of formants.

    The :class:`FormantGenericNormalizer` should be used as the base
    class for normalizers whose implementation does not need
    to distinguish between specific formants.
    """

    def __init__(
            self,
            formants: List[str] = None,
            **kwargs):
        super().__init__(**kwargs)
        self.formants = formants if isinstance(formants, list) else [
            formants] if formants else [f'f{i}' for i in range(0, self.MAX_FX + 1)]

    def _formant_iterator(self):
        yield dict(formants=self.formants)


@docstring
@uninstantiable
class TransformNormalizer(FormantGenericNormalizer):
    """Base class for normalizers which simply transform formants.
    """

    def _norm(self, df):
        transform = self.params.get('transform') or self.config.get('transform')
        if transform:
            formants = self.params.get('formants')
            df[formants] = transform(df[formants])
        return df


@docstring
@uninstantiable
class FormantsTransformNormalizer(TransformNormalizer):
    """Base clase for normalizers transform each formant independently.
    """

    def __init__(
            self,
            formants: List[str] = None,
            transform: Callable[[pd.DataFrame], pd.DataFrame] = None,
            **kwargs):
        super().__init__(formants=formants, transform=transform, **kwargs)


@docstring
@register('default')
@classify(vowel=None, formant=None, speaker=None)
class DefaultNormalizer(FormantGenericNormalizer):
    """'Default' normalizer which returns formant data unaltered.

    Parameters
    ----------
    formants:

    Other parameters
    ----------------
    rename:
    **kwargs:
        Optional keyword arguments passed to the parent constructor.

    Examples
    --------

    .. ipython::

        from vlnm import pb1952, DefaultNormalizer

        df = pb1952(['speaker', 'vowel', 'f1', 'f2'])
        norm_df = DefaultNormalizer(rename='{}*').normalize(df)
        norm_df.head()

    """

    def __init__(
            self,
            formants: List[str] = None,
            rename: Union[str, dict] = None,
            **kwargs):
        super().__init__(formants=formants, rename=rename)

    @docstring
    def normalize(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        return super().normalize(df, **kwargs)


@docstring
@register('chain')
@classify(vowel=None, formant=None, speaker=None)
class ChainNormalizer(Normalizer):
    r"""
    Run multiple normalizers in sequence.

    Parameters
    ----------
    normalizers:
        A list of normalizers.


    Examples
    --------

    .. ipython::

        from vlnm import (
            pb1952,
            ChainNormalizer, BarkNormalizer, LobanovNormalizer)

        df = pb1952(['speaker', 'vowel', 'f1', 'f2'])
        normalizers = [
            BarkNormalizer(rename='{}*'),
            LobanovNormalizer(formants=['f1*', 'f2*'])
        ]
        norm_df = ChainNormalizer(normalizers).normalize(df)
        norm_df.head()


    """

    def __init__(
            self,
            normalizers: Union[List[str], List[Normalizer]] = None):

        super().__init__()
        self.normalizers = normalizers

    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize a DataFrame.

        Parameters
        ----------
        df:
            The DataFrame containing the formant data.

        Returns
        -------
        :
            The normalized data.
        """
        norm_df = df
        for normalizer in self.normalizers:
            try:
                norm_df = normalizer.normalize(norm_df)
            except AttributeError:
                normalizer = get_normalizer(normalizer)
                norm_df = normalizer.normalize(norm_df)
        return norm_df
