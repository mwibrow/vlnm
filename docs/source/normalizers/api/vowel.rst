.. include:: ./defs.rst

.. ipython::
    hidden: yes

    Shell.copy(
        [Sphinx.confdir, '_data', 'pb1952.csv'],
        'pb1952.csv')
    df = pd.read_csv('pb1952.csv')
    df[['speaker', 'vowel', 'f0', 'f1', 'f2', 'f3']].to_csv('vowels.csv', index=False)

:mod:`vlnm.normalizers.vowel`
===============================

.. automodule:: vlnm.normalizers.vowel
    :members:
