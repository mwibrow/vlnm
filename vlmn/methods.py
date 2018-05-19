"""
Normalization methods
"""

import numpy as np
import pandas as pd

def handle_missing(values, policy):
    """
    Handle mising values.

    Parameters
    ----------
    values : float
        Numpy array of values
    policy : str
        One of `'ignore'`, `'mean', `'median'`

    Returns
    -------
    Numpy array.

    Raises
    ------
    Value error if policy is invalid.

    """
    policy = policy.lower()
    if policy == 'ignore':
        return values[np.isfinite(values)]
    elif policy == 'mean':
        values[np.isnan(values)] = np.mean(values[np.isfinite(values)])
        return values
    elif policy == 'median':
        values[np.isnan(values)] = np.median(values[np.isfinite(values)])
    raise ValueError('Unknown missing values policy: {}'.format(policy))

def lobanov(df, vowel, formants, **kwargs):
    """
    Normalize F1 and F2 according to Lobanov

    Parameters
    ----------
    df : DataFrame
        Pandas DataFrame instance containing data for a specific group.
    vowel: str
        Name of the column which contains the vowel labels.
    formants: dict
        A dictionary containing the keys `'f1'` and `'f2'`. The values
        for the keys should be the column or list of columns which
        contain the F1 and F2 formant data.

    Return
    ------
    A dataframe with the normalised formants.

    References
    ----------
    [Lobanov1972] Lobanov, Boris M. 1971. Classification of Russian vowels
        spoken by different listeners.
        Journal of the Acoustical Society of America 49:606-08
    """
    lobanov_df = None
    fmts = [f for fs in zip(formants['f1'], formants['f2']) for f in fs]
    columns = [column for column in df.columns if not column in fmts]
    for fmt in fmts:
        values = handle_missing(
            df[fmt],
            kwargs.get('missing', 'ignore'))
        fmt_mean = np.mean(values)
        fmt_std = np.std(values) or 1.

        fmt_df = df.groupby(by=vowel).apply(
            lambda row: pd.DataFrame({
                fmt: (row[fmt] - fmt_mean) / fmt_std,
                vowel: row[vowel]
            }).merge(row[columns]))

        if lobanov_df is None:
            lobanov_df = fmt_df
        else:
            lobanov_df = lobanov_df.merge(fmt_df)

    return lobanov_df.reset_index(drop=True)