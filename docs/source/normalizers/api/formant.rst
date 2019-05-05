.. include:: ./defs.rst

.. ipython::
    configure:
        dataframe:
            formatters:
                float64: '{:.05f}'
            index: yes
            dtypes:
                speaker: str
                vowel: str
        path: '{tmpdir}'
    before: |
        SetupCsv()
    hidden: yes


:mod:`vlnm.normalizers.formant`
===============================

.. automodule:: vlnm.normalizers.formant
    :members:
