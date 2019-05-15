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
Python versions 3.5 and lower are not supported.
Many operating systems (e.g., Ubuntu Linux and MacOS)
come with Python preinstalled, but it may be
an unsupported version.

If Python is not already installed on your computer
(or it is an unsupported version), the quickest way to get Python set up
is using the |anaconda| distribution, which will also install a number
of useful tools (including |jupyter|).

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

.. code-block:: console

   conda install -c conda-forge shapely

Other solutions and/or workarounds are described below
for different operation systems.

Operating systems
-----------------

|vlnm| should work on any operation system which has a supported
Python version installed. Installation for Linux, MacOS
and Windows are given below.

Currently, |vlnm| can only be installed from github.

Linux
^^^^^

To install |vlnm| use the following command in
a terminal:

.. code-block:: console

   pip install git+https://github.com/mwibrow/vlnm.git


If the installation fails while installing shapely
(typically there will be an error relating to
the GEOS library required by shapely),
the relevant Linux package manager should be
used to install `libgeos`.
For example, Debian-based distributions could use:

.. code-block:: console

   sudo apt-get install libgeos


Then the installation command given above should
be re-run.



MacOS
^^^^^

To install |vlnm| use the following command in
a terminal:

.. code-block:: console

   pip install git+https://github.com/mwibrow/vlnm.git

If the installation fails while installing shapely
(typically there will be an error relating to
the GEOS library required by shapely),
then |homebrew| can be used to install the
GEOS library:

.. code-block:: console

   brew install geos

Then |vlnm| can be installed using the command above.

Windows
^^^^^^^

Everything is more complicated on Windows 🙄

|vlnm| is untested on windows, but experience
suggests that Python should be set up using
|anaconda| and instead of the Windows command
prompt use `Anaconda Prompt`.


After using the ``conda`` command
to install shapely (as described above),
``git`` will need to be installed:

.. code-block:: console

   conda install -c anaconda git

Then |vlnm| can be installed by executing the following
command at the command prompt:


.. code-block:: console

   pip install git+https://github.com/mwibrow/vlnm.git
