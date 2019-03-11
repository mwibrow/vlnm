"""
Vowel normalizer base classes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :mod:`base` module contains the base classes
for vowel normalizers as well as the
:class:`.DefaultNormalizer` which returns data unnormalized
so can be used as a control when comparing normalization methods.

"""
from typing import Callable, List, Union

import pandas as pd

from ..docstrings import docstring
from ..registration import classify, register

FORMANTS = ['f0', 'f1', 'f2', 'f3']


class Normalizer:
    """Base normalizer class.

    The :class:`Normalizer` class forms the base of all
    normalizers and custom normalizers should all interit
    from this class or one of its subclasses.

    Parameters
    ----------
    **kwargs:
        Keyword arguments used by child classes.
    """

    MAX_FX = 5

    config = dict(
        # Required columns for the normalizer.
        columns=[],
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

        # Options set up in normalize method.
        self.options = {}

        # Parameters (configuration and options) supplied to _norm method.
        self.params = {}

        self.formants = ['f0', 'f1', 'f2', 'f3']

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

    @docstring
    def normalize(self, df: pd.DataFrame, rename=None, **kwargs) -> pd.DataFrame:
        """{% normalize %}"""
        self.options = self.default_options.copy()
        self.options.update(
            rename=rename,
            **{key: value for key, value in kwargs.items()
               if value is not None})

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
        norm_df = self._normalize(df)
        self._postnormalize(norm_df)
        return norm_df

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
            renameables = [column for column in norm_df
                           if column not in subset]
            renameables.extend(self.params['formants'])
            rename = self.params.get('rename') or '{}'
            for column in renameables:
                if column in norm_df:
                    try:
                        new_column = rename.get(column, column)
                        if new_column is None:
                            continue
                    except AttributeError:
                        new_column = rename.format(column)

                    df[new_column] = norm_df[column]
        return df

    def _formant_iterator(self):
        yield dict(formants=self.formants)

    def _norm(self, df):  # pylint: disable=no-self-use
        """Implemented by subclasses"""
        return df


@docstring
class FxNormalizer(Normalizer):
    """Base class for normalizers which require specification of individual formants.

    The :class:`FxNormalizer` class should be used as parent class
    for any normalizer which needs to access specific formant
    columns.

    Parameters
    ----------
    {% f0 %}
    {% f1 %}
    {% f2 %}
    {% f3 %}
    """

    MAX_FX = 5

    def __init__(
            self,
            f0: Union[str, List[str]] = 'f0',
            f1: Union[str, List[str]] = 'f1',
            f2: Union[str, List[str]] = 'f2',
            f3: Union[str, List[str]] = 'f3',
            **kwargs):
        super().__init__(**kwargs)
        formants = dict(
            f0=f0 or 'f0',
            f1=f1 or 'f1',
            f2=f2 or 'f2',
            f3=f3 or 'f3')
        for i in range(4, self.MAX_FX + 1):
            fx = f'f{i}'
            if fx in kwargs:
                formants.update(**{fx: kwargs.pop(fx, fx)})
        self.formants = self._sanitize_formants(formants)

    def _sanitize_formants(self, formants):
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


class FormantsNormalizer(Normalizer):
    """Base class for normalizers which require general list of formants.

    The :class:`FormantsNormalizer` should be used as the base
    class for normalizers whose implementation does not need
    to distinguish between specific formants.

    Parameters
    ----------
    {% formants %}
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


class TransformNormalizer(FormantsNormalizer):
    """Base class for normalizers which simply transform formants.
    """

    def _norm(self, df):
        transform = self.params.get('transform') or self.config.get('transform')
        if transform:
            formants = self.params.get('formants')
            df[formants] = transform(df[formants])
        return df


class FormantsTransformNormalizer(TransformNormalizer):
    """Base clase for normalizers transform each formant independently.

    Parameters
    ----------
    {% formants %}
    transform:
        A function which takes |dataframe| containing
        formant data, transforms the data
        and returns (a possibly new) |dataframe|.
    """

    def __init__(
            self,
            formants: List[str] = None,
            transform: Callable[[pd.DataFrame], pd.DataFrame] = None, **kwargs):
        super().__init__(formants=formants, transform=transform, **kwargs)


@docstring
@register('default')
@classify(vowel=None, formant=None, speaker=None)
class DefaultNormalizer(FormantsNormalizer):
    """'Default' normalizer which returns formant data unaltered.

    Parameters
    ----------
    {% formants %}
    {% rename %}

    """

    def __init__(self, formants: List[str] = None, rename: Union[str, dict] = None):
        super().__init__(formants=formants, rename=rename)

    @docstring
    def normalize(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """
        {% normalize %}
        """
        super().normalize(df, **kwargs)
