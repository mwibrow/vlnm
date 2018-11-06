"""
Vowel normalizer module
"""

import pandas as pd

from vlnm.decorators import Parameters

from vlnm.utils import get_formants_spec

def prepare_df(df, columns, aliases):
    """
    Prepare
    """
    for column in columns:
        alias = aliases.get(column)
        if alias and alias in df:
            df[column] = df[alias]
    return df

FORMANTS = ['f0', 'f1', 'f2', 'f3']

class Normalizer:
    """Base normalizer class."""

    transform = None
    required_columns = []
    required_keywords = []

    def __init__(self, f0=None, f1=None, f2=None, f3=None,
                 formants=None, rename=None, groups=None, **kwargs):
        self.kwargs = dict(
            f0=f0,
            f1=f1,
            f2=f2,
            f3=f3,
            formants=formants,
            reanme=rename,
            **kwargs)
        self.columns = []

    def __call__(self, df, **kwargs):
        return self.normalize(df, **kwargs)

    def normalize(self, df, f0=None, f1=None, f2=None, f3=None,
                  formants=None, rename=None, **kwargs):
        """Normalize a dataframe.

        """
        _kwargs = self.kwargs.copy()
        _kwargs.update(kwargs)

        formants_spec = self._get_formants_spec(
            df, f0=f0, f1=f1, f2=f2, f3=f3, formants=formants)

        _kwargs.update(**formants_spec)

        groups = groups or []
        groups.extend(self.actions.keys())
        _kwargs.update(groups=groups, rename=rename or '')

        self._validate(df, **_kwargs)
        return self._normalize(df, **_kwargs)

    def _get_formants_spec(self, df, **kwargs):
        if any(kwargs.get(f) for f in ['f0', 'f1', 'f2', 'f3']):
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
            column = kwargs.get(column, column)
            try:
                if column.strip() not in df:
                    raise ValueError(
                        'Column `{}` not found in data frame'.format(column))
            except AttributeError:
                for col in column:
                    if col not in df:
                        raise ValueError(
                            'Column `{}` not found in data frame'.format(col))


    def _normalize(self, df, **kwargs):
        groups = kwargs.pop('groups', [])
        constants = kwargs.pop('constants', {})
        return self._partition(
            df,
            groups=groups,
            constants=constants,
            columns=self.columns,
            **kwargs)

    def _partition(self, df, groups=None, constants=None, **kwargs):
        if groups:

            norm_df = df.groupby([group], as_index=False).apply(
                lambda gdf, groups=groups[1:], constants=constants:
                self._partition(
                    gdf,
                    groups=groups,
                    constants=constants,
                    **kwargs))
            return norm_df.reset_index(drop=True)
        else:
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
                norm_df = self._norm(
                    df[subset].copy(), constants=constants, **_kwargs)

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
            for f in ['f0', 'f1', 'f2', 'f3']:
                formants.extend(kwargs.get(f, []))
        yield dict(formants=formants)


    @staticmethod
    def _norm(df, **_kwargs):
        return df

class FormantIntrinsicNormalizer(Normalizer):
    """Base class for formant intrinsic normalizers.

    """
    transform = None

    def __init__(self, transform=None, **kwargs):
        super(FormantIntrinsicNormalizer, self).__init__(
            transform=transform or self.__class__.transform,
            **kwargs)

    @staticmethod
    def _formant_iterator(**kwargs):
        formants = kwargs.get('formants')
        if not formants:
            formants = []
            for f in ['f0', 'f1', 'f2', 'f3']:
                formants.extend(kwargs.get(f, []))
        yield dict(formants=formants)

    @staticmethod
    def _norm(df, **kwargs):
        transform = kwargs.get('transform')
        if transform:
            formants = kwargs.get('formants')
            df[formants] = transform(df[formants])
        return df

class FormantExtrinsicNormalizer(Normalizer):
    """Base class for formant extrinsic normalizers."""

    @staticmethod
    def _formant_iterator(**kwargs):
        formant_list = [kwargs.get('f{}'.format(i), [None]) for i in range(4)]
        length = max(len(formant) for formant in formant_list)
        for item in formant_list:
            item.extend(item[-1:] * (length - len(item)))

        for j in range(length):
            formant_spec = {
                'f{}'.format(i): formant_list[i][j]
                for i in range(len(formant_list))}
            formants = [value for value in formant_spec.values()]
            formant_spec.update(formants=formants)
            yield formant_spec
