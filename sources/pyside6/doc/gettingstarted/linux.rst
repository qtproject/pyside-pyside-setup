Getting Started on Linux
==========================

Requirements
------------

* GCC
* ``sphinx`` package for the documentation (optional).
* Depending on your linux distribution, the following dependencies might also be required:

  * ``libgl-dev``, ``python-dev``, ``python-distutils``, and ``python-setuptools``.
* Check the platform dependencies of `Qt for Linux/X11`_.

Building from source
--------------------

Creating a virtual environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``venv`` module allows you to create a local, user-writeable copy of a python environment into
which arbitrary modules can be installed and which can be removed after use::

    python -m venv testenv
    source testenv/bin/activate

will create and use a new virtual environment, which is indicated by the command prompt changing.

Setting up CLANG
~~~~~~~~~~~~~~~~

If you don't have libclang already in your system, you can download from the Qt servers::

    wget https://download.qt.io/development_releases/prebuilt/libclang/libclang-release_140-based-linux-Rhel8.2-gcc9.2-x86_64.7z

Extract the files, and leave it on any desired path, and set the environment
variable required::

    7z x libclang-release_140-based-linux-Rhel8.2-gcc9.2-x86_64.7z
    export LLVM_INSTALL_DIR=$PWD/libclang

Getting the source
~~~~~~~~~~~~~~~~~~

Cloning the official repository can be done by::

    git clone https://code.qt.io/pyside/pyside-setup

Checking out the version that we want to build, for example 6.5::

    cd pyside-setup && git checkout 6.5

Install the general dependencies::

    pip install -r requirements.txt

.. note:: Keep in mind you need to use the same version as your Qt installation.
          Additionally, :command:`git checkout -b 6.5 --track origin/6.5` could be a better option
          in case you want to work on it.

Building and Installing (setuptools)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``setuptools`` approach uses the ``setup.py`` file to execute the build,
install, and packaging steps.

Check your Qt installation path, to specifically use that version of qtpaths to build PySide.
for example, :command:`/opt/Qt/6.5.0/gcc_64/bin/qtpaths`.

Build can take a few minutes, so it is recommended to use more than one CPU core::

    python setup.py build --qtpaths=/opt/Qt/6.5.0/gcc_64/bin/qtpaths --build-tests --ignore-git --parallel=8

To install on the current directory, just run::

    python setup.py install --qtpaths=/opt/Qt/6.5.0/gcc_64/bin/qtpaths --build-tests --ignore-git --parallel=8

Building and Installing (cmake)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``setuptools`` approach includes internal ``CMake`` calls when
building and installing the project, but a CMake-only approach is only
recommended for packaging the project for distribution builds.

Assumming that Qt is in PATH, for example, the configure step can be done with::

    cmake -B /path/to/the/build/directory \
          -S /path/to/the/pyside-setup \
          -DCMAKE_INSTALL_PREFIX=/where/to/install \
          -DPYTHON_EXECUTABLE=/path/to/interpreter

.. note:: You can add `-DFORCE_LIMITED_API=yes` in case you want to have a
   build which will be compatible with Python 3.7+.

and then for building::

    cmake --build /path/to/the/build/directory --parallel X

where `X` is the amount of processes you want to use.
Finally, the install step can be done with::

    cmake --install /path/to/the/build/directory

.. note:: You can build only pyside6 or only shiboken6 by using
   the diferent source directories with the option `-S`.


Test installation
~~~~~~~~~~~~~~~~~

You can execute one of the examples to verify the process is properly working.
Remember to properly set the environment variables for Qt and PySide::

    python examples/widgets/widgets/tetrix.py

.. _`Qt for Linux/X11`: https://doc.qt.io/qt-6/linux.html
