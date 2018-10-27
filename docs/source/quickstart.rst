.. include:: defs.rst

Quick start
============

In the simplest case, |vlnm|

>>> from vlnm import LobanovNormalizer
>>> import pandas as pd
>>> df = pd.read_csv('data.csv')
>>> df.head()
>>> df_norm = LobanovNormalizer().normalize(df)
>>> df.head()