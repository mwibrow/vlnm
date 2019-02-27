.. include:: ./defs.rst

.. _section_installation:

Installation
============

|vlnm| was written using Python version 3.6,
but should work on any version of Python >= 3.0.
Python versions 2.7 and lower are not supported.

For people with little or no experience with
Python or who are unsure how to set up the correct version
of Pyton, the quickest way to get Python set up
is using |anaconda|, which will also install a number
of useful tools (including |jupyter|).
However, it will be necessary to install ``pip`` manually
in order to install |vlnm|.

|vlnm| depends on the 3rd party |shapely| library for some
calculations using in creating vowel plots
(i.e., generating convex hulls).
The installation of this package (which is carried out
automatically when installing |vlnm| can be... tempermental
depending the operation system used.
if Python was installed using
Anaconda then shapely should be installed first
using:

.. code::

    conda install shapely

Other solutions and/or workarounds are described below
for different operation systems.

Linux
-----

To install |vlnm| use the following command in
a terminal:

.. code::

    pip3 install vlnm

If the installation fails while installing shapely
(typically there will be an error relating to
the GEOS library required by shapely), then
the relevant Linux package manager should be
used to install `libgeos`).

MacOS
-----

To install |vlnm| use the following command in
a terminal:

.. code::

    pip3 install vlnm

If the installation fails while installing shapely
(typically there will be an error relating to
the GEOS library required by shapely), then
then |homebrew| can be used to install the
GEOS library:

.. code::

    brew install geos

Then |vlnm| can be installed using the command above.

Windows
-------

Everything is harder on Windows 🙄.

|vlnm| is untested on windows, but experience
suggests that Python should be set up using
|anaconda|.
