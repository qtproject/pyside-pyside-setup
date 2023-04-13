Getting Started on Windows
==========================

The Qt library has to be built with the same version of MSVC as Python and PySide, this can be
selected when using the online installer.

Requirements
------------

* `MSVC2022`_ or (MSVC2019) for Python 3 on Windows,
* `OpenSSL`_ (optional for SSL support, Qt must have been configured using the same SSL library).
* ``sphinx`` package for the documentation (optional).
* Check the platform dependencies of `Qt for Windows`_.

.. note:: Python 3.8.0 was missing some API required for PySide/Shiboken so it's not possible
    to use it for a Windows build.

.. _MSVC2022: https://visualstudio.microsoft.com/downloads/
.. _OpenSSL: https://sourceforge.net/projects/openssl/
.. _`Qt for Windows`: https://doc.qt.io/qt-6/windows.html

Building from source on Windows 10
----------------------------------

Creating a virtual environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``venv`` module allows you to create a local, user-writeable copy of a python environment into
which arbitrary modules can be installed and which can be removed after use::

    python -m venv testenv
    call testenv\Scripts\activate

will create and use a new virtual environment, which is indicated by the command prompt changing.

Setting up CLANG
~~~~~~~~~~~~~~~~

libclang can be downloaded from the
`Qt servers <https://download.qt.io/development_releases/prebuilt/libclang>`_.
for example, ``libclang-release_140-based-windows-vs2019_64.7z``.

Note that from version 12 onwards, the prebuilt Windows binaries from
`LLVM <https://www.llvm.org>`_ no longer contain CMake configuration files; so
they can no longer be used.

Extract the files, and leave it on any desired path, for example, ``c:``,
and set the environment variable required::

    set LLVM_INSTALL_DIR=c:\libclang
    set PATH=C:\libclang\bin;%PATH%

Getting PySide
~~~~~~~~~~~~~~

Cloning the official repository can be done by::

    git clone https://code.qt.io/pyside/pyside-setup

Checking out the version that we want to build, for example, 6.4::

    cd pyside-setup && git checkout 6.4

Install the general dependencies::

    pip install -r requirements.txt

.. note:: Keep in mind you need to use the same version as your Qt installation

Building PySide
~~~~~~~~~~~~~~~

Check your Qt installation path, to specifically use that version of qtpaths to build PySide.
for example, ``C:\Qt\6.4.2\msvc2019_64\bin\qtpaths.exe``.

Build can take a few minutes, so it is recommended to use more than one CPU core::

    python setup.py build --qtpaths=c:\path\to\qtpaths.exe --openssl=c:\path\to\openssl\bin --build-tests --ignore-git --parallel=8

.. _creating_windows_debug_builds:

Creating Debug Builds
~~~~~~~~~~~~~~~~~~~~~

* Choose *Custom Installation* when installing Python and tick the options for
  debug binaries and libraries

* Use ``venv`` to create a virtual environment and pass the debug binary::

   python_d.exe -m venv testenv_d

* Use ``python_d.exe`` to invoke ``setup.py``


Installing PySide
~~~~~~~~~~~~~~~~~

To install on the current directory, just run::

    python setup.py install --qtpaths=c:\path\to\qtpaths.exe  --openssl=c:\path\to\openssl\bin --build-tests --ignore-git --parallel=8

Test installation
~~~~~~~~~~~~~~~~~

You can execute one of the examples to verify the process is properly working.
Remember to properly set the environment variables for Qt and PySide::

    python examples/widgets/widgets/tetrix.py
