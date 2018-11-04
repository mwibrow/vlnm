"""
Vowel normalizer module
"""

import pandas as pd

from vlnm.decorators import Parameters
from vlnm.validation import (
    validate_columns,
    validate_keywords)

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

    required_keywords = []
    iterate_formants = False

    def __init__(
            self,
            formants=None,
            f0=None,
            f1=None,
            f2=None,
            f3=None,
            rename=None,
            groups=None,
            **kwargs):
        self.kwargs = dict(
            formants=formants,
            f0=f0,
            f1=f1,
            f2=f2,
            f3=f3,
            groups=groups,
            reanme=rename,
            **kwargs)
        self.actions = {}
        self.columns = []

    def __call__(self, df, **kwargs):
        return self.normalize(df, **kwargs)

    def normalize(
            self,
            df,
            formants=None,
            f0=None,
            f1=None,
            f2=None,
            f3=None,
            groups=None,
            rename=None,
            **kwargs):
        """Normalize a dataframe.

        """
        options = self.kwargs.copy()
        options.update(
            formants=formants,
            f0=f0,
            f1=f1,
            f2=f2,
            f3=f3,
            groups=groups or [],
            rename=rename or '',
            **kwargs)
        self._validate(df, **options)
        return self._normalize(df, **options)

    def _validate(self, _df, **kwargs):
        for keyword in self.required_keywords:
            if not keyword in kwargs:
                raise ValueError('{} requires keyword {}'.format(
                    self.__class__.__name__, keyword))

    def _normalize(self, df, **kwargs):
        formants = get_formants_spec(
            kwargs.pop('formants', None),
            kwargs.pop('f0', 'f0'),
            kwargs.pop('f1', 'f1'),
            kwargs.pop('f2', 'f2'),
            kwargs.pop('f3', 'f3'),
            df.columns)
        groups = kwargs.pop('groups', [])
        constants = kwargs.pop('constants', {})
        kwargs = kwargs.copy()
        kwargs.update(**formants)
        return self._partition(
            df,
            groups=groups,
            constants=constants,
            columns=self.columns,
            **kwargs)

    def _partition(self, df, groups=None, constants=None, **kwargs):
        if groups:
            group = groups[0]
            if group[-1] in self.actions:
                self.actions[group](df, constants=constants, **kwargs)
            norm_df = df.groupby(group, as_index=False).apply(
                lambda gdf, groups=groups[1:], constants=constants:
                self._partition(
                    gdf,
                    groups=groups,
                    constants=constants,
                    **kwargs))
            return norm_df.reset_index(drop=True)
        else:
            for formant_spec in self._formant_iterator(**kwargs):
                nkwargs = kwargs.copy()
                nkwargs.update(**formant_spec)
                subset = formant_spec['formants'][:]
                subset.extend(kwargs.get('columns', []))
                subset = [column for column in subset if column in df]
                norm_df = self._norm(
                    df[subset].copy(), constants=constants, **kwargs)
                renameables = [column for column in norm_df
                               if column not in subset]
                renameables.extend(formant_spec['formants'])
                rename = kwargs.get('rename') or '{}'
                for column in renameables:
                    if column in norm_df:
                        df[rename.format(column)] = norm_df[column]
            return df

    @staticmethod
    def _formant_iterator(**kwargs):
        formants = kwargs.get('formants')
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


class VowelNormalizer:
    """
    Base class for vowel normalizers.
    """
    _columns = Parameters()
    _keywords = Parameters()
    _name = ''
    _returns = []

    def __init__(self, **kwargs):
        self.default_kwargs = kwargs
        self.actions = {}
        self.groups = kwargs.pop('groups', [])

    @classmethod
    def get_columns(cls):
        """
        Return the column specification for this cass
        """
        return cls._columns

    @classmethod
    def get_keywords(cls):
        """
        Return the keywords specification for this cass
        """
        return cls._keywords

    def validate(self, df, aliases, **options):
        """
        Validate the arguments given to the normalize method.
        """
        validate_columns(
            self._name or self.__class__.__name__,
            df,
            self._columns,
            aliases,
            **options)

        validate_keywords(
            self._name or self.__class__.__name__,
            self._keywords,
            options)

    def normalize(self, df, **kwargs):
        """
        Normalize the formant data in a data frame.
        """
        options = {}
        options.update(self.default_kwargs, **kwargs)

        formants = options.pop('formants', [])
        if not formants:
            formants = [kwargs.get(formant) for formant in FORMANTS
                        if formant in kwargs]
        if not formants:
            formants = [formant for formant in FORMANTS if formant in df]
        aliases = options.pop('aliases', {})
        columns = (set(self._columns.as_list() + FORMANTS)
                   if self._columns else FORMANTS)
        for column in columns:
            alias = kwargs.pop(column, None)
            if alias:
                aliases[column] = alias

        groups = options.pop('groups', [])
        groups.extend(aliases.get(group, group) for group in self.groups)
        constants = options.pop('constants', {})
        actions = options.pop('actions', {})
        actions.update(self.actions)

        self.validate(df, aliases, **options)

        options.update(
            formants=formants,
            groups=groups,
            actions=actions,
            constants=constants,
            aliases=aliases
        )
        self.pre_partition(df, **options)
        normed_df = self.partition(df, **options)
        return self.post_partition(normed_df, **options)

    def pre_partition(self, df, **_):  # pylint: disable=no-self-use
        """
        Process data prior to partitioning.
        """
        return df

    def post_partition(self, df, **_):  # pylint: disable=no-self-use
        """
        Process data after partitioning.
        """
        return df

    def partition(self, df, **kwargs):
        """
        Partition the data frame for normalistion.
        """
        formants = kwargs.pop('formants')
        groups = kwargs.pop('groups')
        actions = kwargs.pop('actions')
        constants = kwargs.pop('constants')
        aliases = kwargs.pop('aliases')
        return self._partition(
            df,
            formants,
            groups,
            actions,
            constants,
            aliases,
            **kwargs)

    def _partition(
            self,
            df,
            formants,
            groups,
            actions,
            constants,
            aliases,
            **kwargs):

        if groups:
            group = groups[0]
            grouped = df.groupby(group, as_index=False)
            out_df = pd.DataFrame()
            for _, grouped_df in grouped:
                action = actions.get(group)
                if action:
                    group_df = prepare_df(
                        grouped_df.copy(),
                        formants + groups,
                        aliases)
                    action(
                        group_df,
                        formants=formants,
                        constants=constants,
                        **kwargs)
                normed_df = self._partition(
                    grouped_df.copy(),
                    formants,
                    groups[1:],
                    actions,
                    constants,
                    aliases,
                    **kwargs)
                if normed_df is not None:
                    out_df = pd.concat([out_df, normed_df], axis=0)
            return out_df

        rename = kwargs.get('rename')
        group_df = prepare_df(
            df.copy(),
            formants + groups,
            aliases)

        normed_df = self._norm(
            group_df,
            formants=formants,
            constants=constants,
            aliases=aliases,
            **kwargs)

        returns = self._returns or formants
        rename = kwargs.get('rename')
        if rename:
            for column in returns:
                if column in normed_df:
                    df[rename.format(column)] = normed_df[column]
        else:
            for column in returns:
                if column in normed_df:
                    df[column] = normed_df[column]

        return df


    def _norm(self, df, **_):  # pylint: disable=no-self-use,unused-argument
        return df


class VowelIntrinsicNormalizer(FormantIntrinsicNormalizer):
    """
    Base class for vowel intrinsic normalizers.
    """
