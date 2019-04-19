.. include:: ../defs.rst

.. ipython::
    configure:
        dataframe:
            formatters:
                float64: '{:.05f}'
            index: yes
            dtypes:
                speaker: str
                vowel: str
        before: |
            import matplotlib
            matplotlib.use("agg")
            import pandas as pd
            from vlnm import normalize
        path: '{tmpdir}'
    hidden: yes

    Shell.copy(
        [Sphinx.confdir, '_data', 'pb1952.csv'],
        'pb1952.csv')
    df = pd.read_csv('pb1952.csv')
    df[['speaker', 'vowel', 'f1', 'f2']].to_csv('vowels.csv', index=False)


:mod:`vlnm.normalizers.base`
===============================

.. automodule:: vlnm.normalizers.base
    :members: