Windows
=======

The Qt library has to be built with the same version of MSVC as Python and PySide, this can be
selected when using the online installer.

Requirements
------------

* `MSVC2022`_ for Python 3 on Windows,
* `OpenSSL`_ (optional for SSL support, Qt must have been configured using the same SSL library).
* ``sphinx`` package for the documentation (optional).
* Check the platform dependencies of `Qt for Windows`_.

.. note:: The Python provided by the Microsoft Store is not compatible with PySide. Please
    use https://www.python.org/downloads/ to get a Python Interpreter.

.. _MSVC2022: https://visualstudio.microsoft.com/downloads/
.. _OpenSSL: https://sourceforge.net/projects/openssl/
.. _`Qt for Windows`: https://doc.qt.io/qt-6/windows.html

Building from source on Windows
-------------------------------

Creating a Dev Drive
~~~~~~~~~~~~~~~~~~~~

We recommend using a `Dev Drive`_ for development work on Windows. This is a
special partition with a fast file system that is excluded from virus scanning.

Creating a virtual environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``venv`` module allows you to create a local, user-writable copy of a python environment into
which arbitrary modules can be installed and which can be removed after use::

    python -m venv testenv
    call testenv\Scripts\activate

will create and use a new virtual environment, which is indicated by the command prompt changing.

Alternatively, you can use the `uv`_ tool, which is popular in the Python community for Python
project management. The following command creates a virtual environment using `uv`_::

    uv venv --python <python-version> testenv
    call testenv\Scripts\activate

.. note:: Since the Qt for Python project still uses `setup.py` and not `pyproject.toml`, currently
          `uv` can only be used as a replacement for `pyenv` for building Qt for Python. If you
          have already the `.python_version` file (used by .pyenv) in the project, make sure to
          change the version to the `uv`_ Python you want to use.

Setting up CLANG
~~~~~~~~~~~~~~~~

libclang can be downloaded from the
`Qt servers <https://download.qt.io/development_releases/prebuilt/libclang>`_.
for example, ``libclang-release_20.1.3-based-windows-vs2019_64.7z``.

For ARM64 Windows, use:
``libclang-release_20.1.3-based-windows-vs2022_arm64.7z``.

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

Checking out the version that we want to build, for example, 6.10::

    cd pyside-setup && git checkout 6.10

Install the general dependencies::

    pip install -r requirements.txt

For building the documentation::

    pip install -r requirements-doc.txt

.. note:: Keep in mind you need to use the same version as your Qt installation

.. note:: With `uv`_, use `uv pip install ...`

Building PySide
~~~~~~~~~~~~~~~

Check your Qt installation path, to specifically use that version of qtpaths to build PySide.
for example, ``C:\Qt\6.10.0\msvc2022_64\bin\qtpaths.exe``.

Build can take a few minutes, so it is recommended to use more than one CPU core::

    python setup.py build --qtpaths=c:\path\to\qtpaths.exe --openssl=c:\path\to\openssl\bin --build-tests --ignore-git --parallel=8

With `uv`_, this command becomes::

    uv run setup.py build --qtpaths=c:\path\to\qtpaths.exe --openssl=c:\path\to\openssl\bin --build-tests --ignore-git --parallel=8


.. _creating_windows_debug_builds:

Creating Debug Builds
~~~~~~~~~~~~~~~~~~~~~

* Choose *Custom Installation* when installing Python and tick the options for
  debug binaries and libraries

* Use ``venv`` to create a virtual environment and pass the debug binary::

   python_d.exe -m venv testenv_d

* Use ``python_d.exe`` to invoke ``setup.py``

.. note:: Make sure you add the ``--debug`` option to the ``python setup.py install`` to produce a debug build


Installing PySide
~~~~~~~~~~~~~~~~~

First, create the wheels using the `create_wheels.py`_ script::

    python create_wheels.py --build-dir=C:\directory\where\pyside\is\built --no-examples

On successful completion, the wheels will be created in the `dist` directory.

.. note:: The `build-dir` typically looks like `build\<your_python_environment_name>`. The
          requirement is that this `build-dir` should contain the `packages_for_wheel` directory.
          If the `python setup.py` build command was successful, this directory should be present.

Finally, to install the wheels, use the following command::

    pip install dist\*.whl


Test installation
~~~~~~~~~~~~~~~~~

You can execute one of the examples to verify the process is properly working.
Remember to properly set the environment variables for Qt and PySide::

    python examples\widgets\widgets\tetrix\tetrix.py

.. _`uv`: https://docs.astral.sh/uv/
.. _`Dev Drive`: https://learn.microsoft.com/en-us/windows/dev-drive/
