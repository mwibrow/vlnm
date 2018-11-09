"""
Vowel normalizer module
"""

from vlnm.utils import get_formants_spec

FORMANTS = ['f0', 'f1', 'f2', 'f3']

class Normalizer:
    """Base normalizer class."""

    transform = None
    groups = []
    required_columns = []
    required_keywords = []

    options = dict()

    def __init__(self, f0=None, f1=None, f2=None, f3=None,
                 formants=None, rename=None, **kwargs):
        kwargs.update(**self.options)
        self.kwargs = dict(
            f0=f0,
            f1=f1,
            f2=f2,
            f3=f3,
            formants=formants,
            rename=rename,
            **kwargs)
        self.columns = []

    def __call__(self, df, **kwargs):
        return self.normalize(df, **kwargs)

    def normalize(self, df, f0=None, f1=None, f2=None, f3=None,
                  formants=None, rename=None, **kwargs):
        """Normalize a dataframe.

        Set up arguments and call the internal function _normalize.
        """
        nkwargs = self.kwargs.copy()
        nkwargs.update(kwargs)
        formants_spec = self._get_formants_spec(
            df, f0=f0, f1=f1, f2=f2, f3=f3, formants=formants)
        nkwargs.update(**formants_spec)

        nkwargs.update(
            constants={},
            groups=self.groups or [],
            rename=rename or '',
            transform=kwargs.pop('transform', self.__class__.transform))
        self._validate(df, **nkwargs)

        self._prenormalize(df, **nkwargs)
        norm_df = self._normalize(df, **nkwargs)
        self._postnormalize(norm_df, **nkwargs)
        return norm_df

    def _get_formants_spec(self, df, **kwargs):
        if any(kwargs.get(f) for f in FORMANTS):
            _kwargs = kwargs.copy()
            _kwargs['formants'] = None
            return get_formants_spec(df.columns, **_kwargs)
        elif kwargs.get('formant'):
            return get_formants_spec(df.columns, formants=kwargs['formants'])
        return get_formants_spec(df.columns, **self.kwargs)

    def _validate(self, df, **kwargs):

        for keyword in self.required_keywords:
            if not keyword in kwargs:
                raise ValueError('{} requires keyword {}'.format(
                    self.__class__.__name__, keyword))
        for column in self.required_columns:
            column = kwargs.get(column, column) or column
            try:
                if column.strip() not in df:
                    raise ValueError(
                        'Column `{}` not found in data frame'.format(column))
            except AttributeError:
                for col in column:
                    if col not in df:
                        raise ValueError(
                            'Column `{}` not found in data frame'.format(col))


    @staticmethod
    def _prenormalize(df, **_kwargs):
        """Actions performed before normalization."""
        return df

    @staticmethod
    def _postnormalize(df, **_kwargs):
        """Actions performed after normalization."""
        return df

    def _normalize(self, df, groups=None, **kwargs):
        if groups:
            norm_df = df.groupby(by=groups, as_index=False).apply(
                lambda group_df, groups=groups[1:], kwargs=kwargs:
                self._normalize(group_df, groups=groups[1:], **kwargs))
            # norm_df = norm_df.reset_index(drop=True)
            return norm_df
        for formant_spec in self._formant_iterator(**kwargs):
            _kwargs = kwargs.copy()
            _kwargs.update(**formant_spec)

            # Get the columns to subset the dataframe.
            subset = formant_spec['formants'][:]
            for column in self.required_columns:
                if column in formant_spec:
                    subset.extend(formant_spec[column])
                else:
                    subset.append(kwargs.get(column, column))

            # Throw an error if column not in dataframe or just plough on?
            subset = list(
                set(column for column in subset if column in df.columns))
            norm_df = self._norm(df[subset].copy(), **_kwargs)

            # Find new/renameable columns and rename.
            renameables = [column for column in norm_df
                           if column not in subset]
            renameables.extend(_kwargs['formants'])
            rename = kwargs.get('rename') or '{}'
            for column in renameables:
                if column in norm_df:
                    df[rename.format(column)] = norm_df[column]
        return df

    @staticmethod
    def _formant_iterator(**kwargs):
        formants = kwargs.get('formants')
        if not formants:
            formants = []
            for f in FORMANTS:
                formants.extend(kwargs.get(f, []))
        yield dict(formants=formants)


    @staticmethod
    def _norm(df, **_kwargs):
        return df


class SimpleTransformable:
    """Base class for normalizers which simply transform formants.

    Provides a :code:`_norm` method which transforms
    all formants together.
    """

    @staticmethod
    def _norm(df, **kwargs):
        transform = kwargs.get('transform')
        if transform:
            formants = kwargs.get('formants')
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
        if not formants:
            formants = []
            for f in FORMANTS:
                formants.extend(kwargs.get(f, []))
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
    required_columns = ['speaker']
    groups = ['speaker']
