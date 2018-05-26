"""
Normalization methods
"""

import numpy as np
import pandas as pd

from vlmn.utils import flatten
from vlmn.normalize import sanitize_formants

def lobanov(df, formants=None, speaker='speaker', vowel='vowel', margins=None, **kwargs):
    r"""
    Normalize F1 and F2 according to [Lobanov1972]

    ..math::

        F_i = \displayfrac{F_i - \mu_i}{\sigma_i}

    Where :math:`mu_i` is the mean of the ith formants for a speaker,
    and :math:`sigma_i` is the standard deviation.

    Parameters
    ----------
    df : DataFrame
        Pandas DataFrame instance containing data for a specific group.

    Keyword Parameters
    ------------------
    formants: list[str] or dict
        A list of the columns that contain formant data.
    f1: str / list[str]
        Alternative key for specifying the column for F1 data.
    f2: str / list[str]
        Alternative key for specifying the column for F2 data.
    f3: str / list[str]
        Alternative key for specifying the column for F3 data.
    speaker: str
        Name of the column which contains the speaker labels.
    vowel: str
        Name of the column which contains the vowel labels.
    margins: list[str]
        Other columns to group the data over.
    suffix: str
        By default, formant columns are replaced by their normalized
        values;
        Specify a suffix for the

    Return
    ------
    A dataframe with the normalised formants.

    References
    ----------
    [Lobanov1972] Lobanov, Boris M. 1971. Classification of Russian vowels
        spoken by different listeners.
        Journal of the Acoustical Society of America 49:606-08
    """
    margins = margins or []
    margins.extend([speaker, vowel])
    grouped = df.groupby(margins or dict(level=0))
    norm_df = pd.DataFrame()

    cols_in = flatten(sanitize_formants(formants, **kwargs))
    cols_out = formants
    suffix = kwargs.pop('suffix')
    if suffix:
        cols_out = ['{}{}'.format(col, suffix) for col in cols_out]
    for _, group_df in grouped:
        mean_f = np.mean(group_df[cols_in])
        std_f = np.std(group_df[cols_in])
        group_norm_df = group_df.copy()
        group_norm_df[cols_out] = (group_df[cols_in] - mean_f) / std_f
        norm_df = pd.concat([
            norm_df,
            group_norm_df
        ])
    return norm_df

def nordstrom(
        df,
        formants=None,
        speaker='speaker',
        vowel='vowel',
        gender='gender',
        female='F',
        margins=None, **kwargs):
    r"""
    Normalize F1 and F2 according to

    ..math::

        F_i = F_i \left(
                1 + I(F_i)\left(
                    \displayfrac{
                        \mu_{F_3}^{\mbox{male}}
                    }{
                        \mu_{F_3}^{\mbox{female}}
                    }
                \right)
            \right

    Where :math:`\mu_{F_3}` is the mean :math:`F_3` across
    all vowels where :math:`F_1` is greater than 600Hz,
    and :math:`I(F_i)` is an indicator function which
    returns 1 if :math:`F_i` is from a female speaker,
    and 0 otherwise.


    Parameters
    ----------
    df : DataFrame
        Pandas DataFrame instance containing data for a specific group.

    Keyword Parameters
    ------------------
    formants: list[str] or dict
        A list of the columns that contain formant data.
    f0: str / list[str]
        alternative key for specifying the column for F0 data.
    f1: str / list[str]
        Alternative key for specifying the column for F1 data.
    f2: str / list[str]
        Alternative key for specifying the column for F2 data.
    f3: str / list[str]
        Alternative key for specifying the column for F3 data.
    speaker: str
        Name of the column which contains the speaker labels.
    vowel: str
        Name of the column which contains the vowel labels.
    margins: list[str]
        Other columns to group the data over.
    suffix: str
        By default, formant columns are replaced by their normalized
        values;
        Specify a suffix for the

    Return
    ------
    A dataframe with the normalised formants.

    References
    ----------

    """
    margins = margins or []

    cols_in = flatten(sanitize_formants(formants, **kwargs))
    cols_out = formants
    suffix = kwargs.pop('suffix')
    if suffix:
        cols_out = ['{}{}'.format(col, suffix) for col in cols_out]

    fmts_in = cols_in[0]
    fmts_out = cols_out[0]

    grouped = df.groupby(margins, as_index=False) if margins else (None, df)
    norm_df = pd.DataFrame()
    for _, group_df in grouped:
        for fmts_in, fmts_out in zip(cols_in, cols_out):
            mu_f3_male = group_df.loc[
                (group_df[fmts_in[1] > 600]) & (group_df[gender] != female),
                [fmts_in[3]]].mean()
            mu_f3_female = group_df.loc[
                (group_df[fmts_in[1] > 600]) & (group_df[gender] == female),
                [fmts_in[3]]].mean()

            mu_quotient = mu_f3_male / mu_f3_female
            subgrouped = group_df.groupby([speaker, vowel], as_index=False)

            fmt_in = [fmt for fmt in fmts_in if fmt]
            fmt_out = [fmt for fmt in fmts_out if fmt]

            for _, subgroup_df in subgrouped:
                subgroup_norm_df = pd.DataFrame()
                indicator = (subgroup_df[gender] == female).astype(float).values
                subgroup_norm_df[fmt_out] = subgroup_df[fmt_in] * (1 + indicator * mu_quotient)
                norm_df = pd.concat([
                    norm_df,
                    subgroup_norm_df
                ])
    return norm_df


def lce(df, formants=None, speaker='speaker', vowel='vowel', margins=None, **kwargs):
    r"""
    Normalize F1 and F2 according to

    ..math::

        F_i = \displayfrac{F_i}{\max(F_i)}

    Parameters
    ----------
    df : DataFrame
        Pandas DataFrame instance containing normalized formants.

    Keyword Parameters
    ------------------
    formants: list[str] or dict
        A list of the columns that contain formant data.
    f0: str / list[str]
        alternative key for specifying the column for F0 data.
    f1: str / list[str]
        Alternative key for specifying the column for F1 data.
    f2: str / list[str]
        Alternative key for specifying the column for F2 data.
    f3: str / list[str]
        Alternative key for specifying the column for F3 data.
    speaker: str
        Name of the column which contains the speaker labels.
    vowel: str
        Name of the column which contains the vowel labels.
    margins: list[str]
        Other columns to group the data over.
    suffix: str
        By default, formant columns are replaced by their normalized
        values;
        Specify a suffix for the

    Return
    ------
    A dataframe with the normalised formants.

    References
    ----------

    """
    margins = margins or []
    margins.extend([speaker, vowel])
    grouped = df.groupby(margins or dict(level=0))
    norm_df = pd.DataFrame()

    cols_in = flatten(sanitize_formants(formants, **kwargs))
    cols_out = formants
    suffix = kwargs.pop('suffix')
    if suffix:
        cols_out = ['{}{}'.format(col, suffix) for col in cols_out]
    for _, group_df in grouped:
        max_f = np.max(group_df[cols_in])
        group_norm_df = group_df.copy()
        group_norm_df[cols_out] = group_df[cols_in] / max_f
        norm_df = pd.concat([
            norm_df,
            group_norm_df
        ])
    return norm_df



def gerstman(df, formants=None, speaker='speaker', vowel='vowel', margins=None, **kwargs):
    r"""
    Normalize F1 and F2 according to

    ..math::

        F_i = \displayfrac{F_i - \min(F_{ij})}{\max(F_{ij}) - \min(F_{ij})}

    Where :math:`mu_i` is the mean of the ith formants for a speaker,
    and :math:`sigma_i` is the standard deviation.

    Parameters
    ----------
    df : DataFrame
        Pandas DataFrame instance containing data for a specific group.

    Keyword Parameters
    ------------------
    formants: list[str] or dict
        A list of the columns that contain formant data.
    f0: str / list[str]
        alternative key for specifying the column for F0 data.
    f1: str / list[str]
        Alternative key for specifying the column for F1 data.
    f2: str / list[str]
        Alternative key for specifying the column for F2 data.
    f3: str / list[str]
        Alternative key for specifying the column for F3 data.
    speaker: str
        Name of the column which contains the speaker labels.
    vowel: str
        Name of the column which contains the vowel labels.
    margins: list[str]
        Other columns to group the data over.
    suffix: str
        By default, formant columns are replaced by their normalized
        values;
        Specify a suffix to keep the original columns.

    Return
    ------
    A dataframe with the normalised formants.

    References
    ----------

    """
    margins = margins or []
    margins.extend([speaker, vowel])
    grouped = df.groupby(margins or dict(level=0))
    norm_df = pd.DataFrame()

    cols_in = flatten(sanitize_formants(formants, **kwargs))
    cols_out = formants
    suffix = kwargs.pop('suffix')
    if suffix:
        cols_out = ['{}{}'.format(col, suffix) for col in cols_out]
    for _, group_df in grouped:
        max_f = np.max(group_df[cols_in])
        min_f = np.min(group_df[cols_in])
        group_norm_df = group_df.copy()
        group_norm_df[cols_out] = (group_df[cols_in] - min_f) / (max_f - min_f)
        norm_df = pd.concat([
            norm_df,
            group_norm_df
        ])
    return norm_df


def neary1(df, formants=None, speaker='speaker', vowel='vowel', margins=None, **kwargs):
    """
    Normalize formants according to [Neary]

    Parameters
    ----------
    df : DataFrame
        Pandas DataFrame instance containing data for a specific group.
    vowel: str
        Name of the column which contains the vowel labels.
    formants: dict
        A dictionary containing the keys `'f1'`, `'f2'` and/or `'f3'`. The values
        for the keys should be the column or list of columns which
        contain the formant data.

    Return
    ------
    A dataframe with the normalised formants.

    References
    ----------

    """
    margins = margins or []

    cols_in = flatten(sanitize_formants(formants, **kwargs))
    cols_out = formants
    suffix = kwargs.pop('suffix')
    if suffix:
        cols_out = ['{}{}'.format(col, suffix) for col in cols_out]

    norm_df = pd.DataFrame()

    margins.extend([speaker])
    grouped = df.groupby(margins, as_index=False)

    for _, group_df in grouped:
        fmt_mean = np.log(df[cols_in].mean())

        subgrouped = group_df.groupby(by='vowel', as_index=False)
        for _, subgroup_df in subgrouped:
            subgroup_norm_df = subgroup_df.copy()
            subgroup_norm_df[cols_out] = np.log(subgroup_norm_df[cols_out]) - fmt_mean
            norm_df = pd.concat([
                norm_df,
                subgroup_norm_df
            ])

    return norm_df.reset_index(drop=True)


def neary2(df, formants=None, speaker='speaker', vowel='vowel', margins=None, **kwargs):
    """
    Normalize formants according to [Neary]

    Parameters
    ----------
    df : DataFrame
        Pandas DataFrame instance containing data for a specific group.
    vowel: str
        Name of the column which contains the vowel labels.
    formants: dict
        A dictionary containing the keys `'f1'`, `'f2'` and/or `'f3'`. The values
        for the keys should be the column or list of columns which
        contain the formant data.

    Return
    ------
    A dataframe with the normalised formants.

    References
    ----------

    """
    norm_df = None
    formants = sanitize_formants(formants, **kwargs)
    keys = sorted(formants.keys())
    fmts_list = [[formants[key][i] for key in keys]
            for i in range(len(formants[keys[0]]))]
    for fmts in fmts_list:
        columns = [column for column in df.columns if not column in fmts]
        values = df[fmts][np.isfinite(df[fmts])]
        fmts_mean = np.mean(np.mean(np.log(values)))
        for fmt in fmts:
            fmt_df = df.groupby(by=vowel).apply(
                lambda row: pd.DataFrame({
                    fmt: np.exp(np.log(row[fmt]) - fmts_mean),
                    vowel: row[vowel]
                }).merge(row[columns]))

            if norm_df is None:
                norm_df = fmt_df
            else:
                norm_df = norm_df.merge(fmt_df)

    return norm_df.reset_index(drop=True)


def watt_fabricius(df, formants, **kwargs):
    """
    """
