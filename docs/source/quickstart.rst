.. include:: defs.rst

Quick start
============

Although, some normalizers have more complex requirements,
in the simplest case, you have a CSV file which contains columns
for *speaker*, *vowel*, *F1* and *F2*:

>>> from vlnm import LobanovNormalizer
>>> import pandas as pd
>>> df = pd.read_csv('data.csv')
>>> df.head(n=5)
>>> df_norm = LobanovNormalizer().normalize(df)
>>> df.head(n=5)

Perhaps, you wish to keep the original formant values, in
which case the `rename` keyword argument can be used:

>>> df_norm = LobanovNormalizer().normalize(df, rename='{}N')
>>> df.head(n=5)

.. console:: python

   import pandas as pd
   df = pd.DataFrame(dict(
       a=[1,2,3,4,5,6,7,8,9],
       b=['a','b','c','d','e','f','g','h','i']))
   df.head()
   print('hello')
   print('GOodbye')
   for i in range(10):
       print(i)

   print('And that\'s all folks')

End