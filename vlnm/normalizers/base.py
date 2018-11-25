"""
Vowel normalizer module
"""
from typing import List, Union

from ..docstrings import docstring
from ..utils import get_formants_spec
from . import register_class

FORMANTS = ['f0', 'f1', 'f2', 'f3']


@register_class('default')
class Normalizer(object):
    """Base normalizer class.

    Parameters
    ----------

    {% f0 %}
    {% f1 %}
    {% f2 %}
    {% f3 %}
    {% formants %}
    {% rename %}

    """

    config = dict(
        # Required columns for the normalizer.
        columns=[],
        # Keywords used by the normalizer.
        keywords=[],
        # Default options
        options=dict())

    def __init__(
            self,
            f0: Union[str, List[str]] = None,
            f1: Union[str, List[str]] = None,
            f2: Union[str, List[str]] = None,
            f3: Union[str, List[str]] = None,
            formants: List[str] = None,
            rename: str = None,
            **kwargs):
        # Class configuration.
        self.config = self._get_config()

        # Constructor options.
        self.default_options = self.config.get('options', {}).copy()
        self.default_options.update(
            f0=f0, f1=f1, f2=f2, f3=f3,
            formants=formants,
            rename=rename,
            **kwargs)

        # Options set up in normalize method.
        self.options = {}

        # Parameters (configuration and options) supplied to _norm method.
        self.params = {}


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
    def normalize(self, df, f0=None, f1=None, f2=None, f3=None,
                  formants=None, rename=None, **kwargs):
        """{% normalize %}"""
        self.options = self.default_options.copy()
        self.options.update(
            rename=rename,
            **{key: value for key, value in kwargs.items()
               if value is not None})
        formants_spec = self._get_formants_spec(
            f0=f0, f1=f1, f2=f2, f3=f3, formants=formants)
        self.options.update(**formants_spec)

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

    @staticmethod
    def _get_formants_spec(**kwargs):
        """Derive the formant structure from the given formants."""
        if any(kwargs.get(f) for f in FORMANTS):
            _kwargs = kwargs.copy()
            _kwargs['formants'] = None
            return get_formants_spec(**_kwargs)
        elif kwargs.get('formants'):
            return get_formants_spec(formants=kwargs['formants'])
        return get_formants_spec()

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
        for formant_spec in self._formant_iterator(**self.options):
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
                    df[rename.format(column)] = norm_df[column]
        return df

    @staticmethod
    def _formant_iterator(**kwargs):
        formants = kwargs.get('formants')
        yield dict(formants=formants)

    def _norm(self, df):  # pylint: disable=no-self-use
        """Implemented by subclasses"""
        return df


class SimpleTransformable(Normalizer):
    """Base class for normalizers which simply transform formants.

    Provides a :code:`_norm` method which transforms
    all formants together.
    """

    def _norm(self, df):
        transform = self.params.get('transform', self.config.get('transform'))
        if transform:
            formants = self.params.get('formants')
            df[formants] = transform(df[formants])
        return df


class FormantIntrinsicNormalizer(Normalizer):
    """Base class for formant intrinsic normalizers.

    This provides a :code:`_formant_iterator` method which yields
    a single formant structure for all specified formants.
    """

    @staticmethod
    def _formant_iterator(**kwargs):
        formants = kwargs.get('formants')
        yield dict(formants=formants)


class FormatIntrinsicTransformableNormalizer(
        SimpleTransformable, FormantIntrinsicNormalizer):
    """Base clase for formant intrinsic normalizers with a transform."""


class FormantExtrinsicNormalizer(Normalizer):
    """Base class for formant extrinsic normalizers.

    This provides a :code:`_formant_iterator` method which yields
    a formant structure for sequences of formants.
    """

    @staticmethod
    def _formant_iterator(**kwargs):
        formant_list = [kwargs.get(f) for f in FORMANTS]
        length = max(len(formant) for formant in formant_list if formant)
        for item in formant_list:
            if item:
                item.extend(item[-1:] * (length - len(item)))
        for i in range(length):
            formant_spec = {
                formant: formant_list[j][i]
                for j, formant in enumerate(FORMANTS) if formant_list[j]}
            formants = [value for value in formant_spec.values()]
            formant_spec.update(formants=formants)
            yield formant_spec


class SpeakerIntrinsicNormalizer(FormantExtrinsicNormalizer):
    """Base class for speaker intrinsic normalizers."""

    config = dict(
        columns=['speaker']
    )

    def _normalize(self, df):
        speaker = self.options.get('speaker') or 'speaker'
        return df.groupby(by=speaker, as_index=False).apply(
            super()._normalize)
