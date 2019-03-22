.. include:: ./defs.rst

.. _section_installation:

Installation
============

This part of the documentation covers the installation of |vlnm|.


Prerequisites
-------------

Python
^^^^^^

|vlnm| was written using Python version 3.6,
but should work on any version of Python >= 3.0.
Python versions 2.7 and lower are not supported.
Many operating systems (e.g., Ubuntu Linux and MacOS)
come with Python preinstalled, but it may be
an unsupported version.

If Python is not already installed on your computer
(or it is an unsupported version), the quickest way to get Python set up
is using the |anaconda| distribution, which will also install a number
of useful tools (including |jupyter|).
Having installed Anaconda it may be necesary to install
the Python package manager ``pip3``, by running the
following command in a terminal:

.. ipython::
    :code-only:
    :terminal:

    conda install pip3

However, the Anaconda distribution is large (to say the least) and
includes a considerable number of tools which are not needed
just to normalize vowel formant data and produce vowel plots.
To create a minimal working Python installation,
`The Hitchhiker's Guide to Python <https://docs.python-guide.org/starting/installation/>`_
may provide a useful start.

Shapely
^^^^^^^

|vlnm| depends on the 3rd party |shapely| python library for some
calculations using in creating vowel plots
(i.e., generating convex hulls).
The installation of this package (which is carried out
automatically when installing |vlnm|) can be tempermental
depending the operation system used.
If Python was installed using
Anaconda then shapely should be installed first
using:

.. ipython::
    :terminal:

    conda install shapely

Other solutions and/or workarounds are described below
for different operation systems.

Operating systems
-----------------

|vlnm| should work on any operation system which has a supported
Python version installed. Installation for Linux, MacOS
and Windows are given below:

Linux
^^^^^

To install |vlnm| use the following command in
a terminal:

.. ipython::
    :terminal:

    pip3 install vlnm

If the installation fails while installing shapely
(typically there will be an error relating to
the GEOS library required by shapely),
the relevant Linux package manager should be
used to install `libgeos`.
Then the installation command given above should
be re-run.



MacOS
^^^^^

To install |vlnm| use the following command in
a terminal:

.. ipython::
    :terminal:

    pip3 install vlnm

If the installation fails while installing shapely
(typically there will be an error relating to
the GEOS library required by shapely),
then |homebrew| can be used to install the
GEOS library:

.. ipython::
    :terminal:

    brew install geos

Then |vlnm| can be installed using the command above.

Windows
^^^^^^^

Everything is harder on Windows 🙄

|vlnm| is untested on windows, but experience
suggests that Python should be set up using
|anaconda|. After using the ``conda`` command
to install pip3 and shapely (as described above),
|vlnm| can be installed by executing the following
command at the command prompt:

.. ipython::
    :terminal:

    pip3 install vlnm
