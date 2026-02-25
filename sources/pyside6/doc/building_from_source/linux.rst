Linux
=====

Requirements
------------

* GCC
* ``sphinx`` package for the documentation (optional).
* Depending on your linux distribution, the following dependencies might also be required:

  * ``libgl-dev``, ``python-dev``, and ``python-setuptools``.
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

Alternatively, you can use the `uv`_ tool, which is popular in the Python community for Python
project management. The following command creates a virtual environment using `uv`_::

    uv venv --python <python-version> testenv
    source testenv/bin/activate

.. note:: Since the Qt for Python project still uses `setup.py` and not `pyproject.toml`, currently
          `uv` can only be used as a replacement for `pyenv` for building Qt for Python. If you
          have already the `.python-version` file (used by .pyenv) in the project, make sure to
          change the version to the `uv`_ Python you want to use.

Setting up CLANG
~~~~~~~~~~~~~~~~

If you don't have libclang already in your system, you can download from the Qt servers::

    wget https://download.qt.io/development_releases/prebuilt/libclang/libclang-release_20.1.3-based-linux-Rhel8.8-gcc10.3-x86_64.7z

Extract the files, and leave it in any desired path, and set the environment
variable required::

    7z x libclang-release_20.1.3-based-linux-Rhel8.8-gcc10.3-x86_64.7z
    export LLVM_INSTALL_DIR=$PWD/libclang

Getting the source
~~~~~~~~~~~~~~~~~~

Cloning the official repository can be done by::

    git clone https://code.qt.io/pyside/pyside-setup

Checking out the version that we want to build, for example 6.10::

    cd pyside-setup && git checkout 6.10

Install the general dependencies::

    pip install -r requirements.txt

For building the documentation::

    pip install -r requirements-doc.txt

.. note:: Keep in mind you need to use the same version as your Qt installation.
          Additionally, :command:`git checkout -b 6.10 --track origin/6.10` could be a better option
          in case you want to work on it.

.. note:: With `uv`_, use `uv pip install ...`

Building and Installing (setuptools)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``setuptools`` approach uses the ``setup.py`` file to execute the build step and further
uses `create_wheels.py`_ to create the wheels. Once the wheels are created, you can install the
wheels using the `pip` command.

Check your Qt installation path, to specifically use that version of qtpaths to build PySide.
for example, :command:`/opt/Qt/6.10.0/gcc_64/bin/qtpaths`.

Build can take a few minutes, so it is recommended to use more than one CPU core::

    python setup.py build --qtpaths=/opt/Qt/6.10.0/gcc_64/bin/qtpaths --build-tests --ignore-git --parallel=8

With `uv`_, the build command becomes::

    uv run setup.py build --qtpaths=/opt/Qt/6.10.0/gcc_64/bin/qtpaths --build-tests --ignore-git --parallel=8

To create the wheels, just run::

    python create_wheels.py --build-dir=/directory/where/pyside/is/built --no-examples

On successful completion, the wheels will be created in the `dist` directory.

.. note:: The `build-dir` typically looks like `build/<your_python_environment_name>`. The
          requirement is that this `build-dir` should contain the `packages_for_wheel` directory.
          If the `python setup.py` build command was successful, this directory should be present.

Finally, to install the wheels, use the following command::

    pip install dist/*.whl

Building and Installing (cmake)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``setuptools`` approach includes internal ``CMake`` calls when
building and installing the project, but a CMake-only approach is only
recommended for packaging the project for distribution builds.

Assuming that Qt is in PATH, for example, the configure step can be done with::

    cmake -B /path/to/the/build/directory \
          -S /path/to/the/pyside-setup \
          -DCMAKE_INSTALL_PREFIX=/where/to/install \
          -DPython_EXECUTABLE=/path/to/interpreter

.. note:: You can add `-DFORCE_LIMITED_API=yes` in case you want to have a
   build which will be compatible with Python 3.9+.

and then for building::

    cmake --build /path/to/the/build/directory --parallel X

where `X` is the number of processes you want to use.
Finally, the install step can be done with::

    cmake --install /path/to/the/build/directory

.. note:: You can build only pyside6 or only shiboken6 by using
   the different source directories with the option `-S`.


Test installation
~~~~~~~~~~~~~~~~~

You can execute one of the examples to verify the process is properly working.
Remember to properly set the environment variables for Qt and PySide::

    python examples/widgets/widgets/tetrix/tetrix.py

.. _`Qt for Linux/X11`: https://doc.qt.io/qt-6/linux.html
.. _`uv`: https://docs.astral.sh/uv/
.. _`create_wheels.py`: https://code.qt.io/cgit/pyside/pyside-setup.git/tree/create_wheels.py
