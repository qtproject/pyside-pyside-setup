|project| Getting Started
==========================

.. important:: This page is focused on building |project| **from source**.
  If you just want to install |pymodname|, you need to run: :command:`pip install pyside6`.

  For more details, refer to our `Quick Start`_ guide. Additionally, you can check the
  :ref:`FAQ <faq>` related to the project.

.. _Quick Start: quickstart.html

General Requirements
--------------------

The following prerequisites must be installed before you build |project|.
On **Linux** you might get them with your operating system package manager, on **macOS**
you might get them with ``brew``, and on **Windows** you can download the installer from each
website.

 * **Python**: 3.6+ `[official Python website] <https://www.python.org/downloads/>`_
 * **Qt:** 6.0+ `[online installer] <https://download.qt.io/official_releases/online_installers/>`_
 * **CMake:** 3.18+ `[official CMake website] <https://cmake.org/download/>`_
 * **Git:** 2.0+. `[official Git website] <https://git-scm.com/downloads>`_
 * **libclang:** The libclang library, recommended: version 10 for 6.0+.
   Prebuilt versions for each OS can be `downloaded here`_.

.. _downloaded here: https://download.qt.io/development_releases/prebuilt/libclang/

Guides per platform
-------------------

You can refer to the following pages for platform specific instructions:

.. raw:: html

    <table class="special">
        <colgroup>
            <col style="width: 200px" />
            <col style="width: 200px" />
            <col style="width: 200px" />
        </colgroup>
        <tr>
            <td><a href="gettingstarted-windows.html"><p><strong>Windows</strong></p></a></td>
            <td><a href="gettingstarted-macOS.html"><p><strong>macOS</strong></p></a></td>
            <td><a href="gettingstarted-linux.html"><p><strong>Linux</strong></p></a></td>
        </tr>
    </table>

.. important:: |project| does not yet support WebAssembly and the mobile operating systems (Android or iOS).

Most Linux-based embedded OS provide PySide with their official
package manager (for example, `Raspbian`_ and `ArchlinuxARM`_).

.. _Raspbian: https://www.raspbian.org/
.. _ArchlinuxARM: https://archlinuxarm.org/

A normal building command will look like this::

    python setup.py install --qtpaths=/path/to/qtpaths \
                            --ignore-git \
                            --debug \
                            --build-tests \
                            --parallel=8 \
                            --verbose-build \
                            --module-subset=Core,Gui,Widgets

Which will build and install the project with **debug** symbols, including the **tests**,
using **ninja** (instead of make), and considering only the **module subset** of
:mod:`QtCore <PySide6.QtCore>`, :mod:`QtGui <PySide6.QtGui>`, and
:mod:`QtWidgets <PySide6.QtWidgets`.

Other important options to consider are:
 * ``--cmake``, to specify the path to the cmake binary,
 * ``--reuse-build``, to rebuild only the modified files,
 * ``--openssl=/path/to/openssl/bin``, to use a different path for OpenSSL,
 * ``--standalone``, to copy over the Qt libraries into the final package to make it work on other
   machines,
 * ``--doc-build-online``, to build documentation using the online template.

Testing the installation
------------------------

Once the installation finishes, you will be able to execute any of our examples::

  python examples/widgets/widgets/tetrix.py

Running Tests
-------------

Using the ``--build-tests`` option will enable us to run all the auto tests inside the project::

  python testrunner.py test > testlog.txt

.. note:: On Windows, don't forget to have qtpaths in your path
   (:command:`set PATH=E:\\\Path\\\to\\\Qt\\\6.0.0\\\msvc2019_64\\\bin;%PATH%`)

You can also run a specific test (for example ``qpainter_test``) by running::

    ctest -R qpainter_test --verbose

.. _cross_compilation:

Cross Compilation
-----------------

Starting from 6.3, it is possible to cross-compile Shiboken (module), and
PySide.  This functionality is still in Technical Preview, which means it could
change in the future releases.

.. important:: The only supported configuration is using a host Linux
   machine to cross-compile to a Linux target platform.

Cross compiling software is a valid use case that many projects rely on,
however, it is a complicated process that might fail due to many reasons.

Before starting with the process, it is important to understand the details of
the build system, and the goal of cross compilation.

In the build process, a ``Host`` is the computer you are currently using to
compile, and a ``Target`` is your embedded device that you are compiling for.

Qt for Python is being built using setuptools, and relies on a ``setup.py`` file
that is called recursively to build Shiboken (module),
Shiboken (generator), and PySide. As the generator is creating
the wrappers for the bindings, it's not cross compiled
for the target.
Only the Shiboken (module) and PySide are cross compiled.

The building process requires a Qt installation, and a Python interpreter
on both the host, and the target. The used Qt versions on both platforms
should have the same minor version. That is, Qt 6.3 (host)
cannot be used with a Qt 6.2 (target), or the other way around.


Prerequisites
~~~~~~~~~~~~~

First and foremost, you need to have access to the target device because you
need to copy several system files (sysroot).  We recommend a Linux OS that has
the latest Qt versions, like `Manjaro ARM`_ or `Archlinux ARM`_.

* (target) Install Qt 6.3+ on the system using the package manager.
* (host) Install Qt 6.3+ on the system using the package manager or Qt
  Installer.
* (target, host) Install the library and development packages that provide
  C++ headers, linkers, libraries, and compilers.
* (target, host) Install Python interpreter v3.7 or later
* (target, host) Install CMake 3.17+

After installing these prerequisites, copy the ``target`` sysroot to your
``host`` computer. This process is tricky, because copying system files from
another computer might cause problems with the symbolic links.  Here you
have two options to achieve that.

Option A: Copying the files
***************************

Create a directory to copy the sysroot of your target device,
for example ``rpi-sysroot``, and perform the copy on your host computer:

.. code-block:: bash

    rsync -vR --progress -rl --delete-after --safe-links \
        USERNAME@TARGET_IP:/{lib,usr,opt/vc/lib} rpi-sysroot/

Ensure to replace ``USERNAME`` and ``TARGET_IP`` with your system appropriate
values.

Option B: Packaging the file system
***********************************

Create a package for your sysroot in your target:

.. code-block:: bash

    tar cfJ ~/sysroot.tar.xz /lib /usr /opt/vc/lib

Copy the package from the target to your host:

.. code-block:: bash

    rsync -vR --progress USERNAME@TARGET_IP:sysroot.tar.xz .

Once you have the tar file, unpack it inside a ``rpi-sysroot`` directory.

It is recommended to run the following script to fix
most of the issues you would find with symbolic links:

.. code-block:: python

    import sys
    from pathlib import Path
    import os

    # Take a sysroot directory and turn all the absolute symlinks and turn them into
    # relative ones such that the sysroot is usable within another system.

    if len(sys.argv) != 2:
        print(f"Usage is {sys.argv[0]} <sysroot-directory>")
        sys.exit(-1)

    topdir = Path(sys.argv[1]).absolute()

    def handlelink(filep, subdir):
        link = filep.readlink()
        if str(link)[0] != "/":
            return
        if link.startswith(topdir):
            return
        relpath = os.path.relpath((topdir / link).resolve(), subdir)
        os.unlink(filep)
        os.symlink(relpath, filep)

    for f in topdir.glob("**/*"):
        if f.is_file() and f.is_symlink():
            handlelink(f, f.parent)

Setting up the toolchain
~~~~~~~~~~~~~~~~~~~~~~~~

To perform the cross compilation, you need a special set of compilers,
libraries, and headers, which runs on the host architecture, but generates
(binaries/executables) for a target architecture.
For example, from x86_64 to aarch64.

It is recommended to use the official 10.2 `ARM Developer cross compilers`_,
which you can find on their official website. For this tutorial, we choose
``aarch64`` target architecture and we will assume that you downloaded the
`gcc-arm-10.2-2020.11-x86_64-aarch64-none-linux-gnu.tar.xz`_ file,
and unpacked it.

With those compilers, now you need a CMake toolchain file. This is
a configuration file to set the compilers and sysroot information, together
with extra options like compilation flags, and other details.  You can use the
following file as an example, but keep in mind they might vary:

.. code-block:: cmake

    # toolchain-aarch64.cmake
    cmake_minimum_required(VERSION 3.18)
    include_guard(GLOBAL)

    set(CMAKE_SYSTEM_NAME Linux)
    set(CMAKE_SYSTEM_PROCESSOR aarch64)

    set(TARGET_SYSROOT /path/to/your/target/sysroot)
    set(CROSS_COMPILER /path/to/your/crosscompiling/compilers/)

    set(CMAKE_SYSROOT ${TARGET_SYSROOT})

    set(ENV{PKG_CONFIG_PATH} "")
    set(ENV{PKG_CONFIG_LIBDIR} ${CMAKE_SYSROOT}/usr/lib/pkgconfig:${CMAKE_SYSROOT}/usr/share/pkgconfig)
    set(ENV{PKG_CONFIG_SYSROOT_DIR} ${CMAKE_SYSROOT})

    set(CMAKE_C_COMPILER ${CROSS_COMPILER}/aarch64-none-linux-gnu-gcc)
    set(CMAKE_CXX_COMPILER ${CROSS_COMPILER}/aarch64-none-linux-gnu-g++)

    set(QT_COMPILER_FLAGS "-march=armv8-a")
    set(QT_COMPILER_FLAGS_RELEASE "-O2 -pipe")
    set(QT_LINKER_FLAGS "-Wl,-O1 -Wl,--hash-style=gnu -Wl,--as-needed")

    set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
    set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
    set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
    set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)

    include(CMakeInitializeConfigs)

    function(cmake_initialize_per_config_variable _PREFIX _DOCSTRING)
      if (_PREFIX MATCHES "CMAKE_(C|CXX|ASM)_FLAGS")
        set(CMAKE_${CMAKE_MATCH_1}_FLAGS_INIT "${QT_COMPILER_FLAGS}")

        foreach (config DEBUG RELEASE MINSIZEREL RELWITHDEBINFO)
          if (DEFINED QT_COMPILER_FLAGS_${config})
            set(CMAKE_${CMAKE_MATCH_1}_FLAGS_${config}_INIT "${QT_COMPILER_FLAGS_${config}}")
          endif()
        endforeach()
      endif()

      if (_PREFIX MATCHES "CMAKE_(SHARED|MODULE|EXE)_LINKER_FLAGS")
        foreach (config SHARED MODULE EXE)
          set(CMAKE_${config}_LINKER_FLAGS_INIT "${QT_LINKER_FLAGS}")
        endforeach()
      endif()

      _cmake_initialize_per_config_variable(${ARGV})
    endfunction()

You need to adjust the paths in these two lines::

    set(TARGET_SYSROOT /path/to/your/target/sysroot)
    set(CROSS_COMPILER /path/to/your/crosscompiling/compilers/)

and replace them with the sysroot directory (the one we called ``rpi-sysroot``),
and the compilers (the ``gcc-arm-10.2-2020.11-x86_64-aarch64-none-linux-gnu/bin`` directory).


Cross compiling PySide
~~~~~~~~~~~~~~~~~~~~~~

After you have installed the prerequisites and copied the necessary files, you
should have the following:

* The compilers to cross compile (``gcc-argm-10.2-...``),
* The target sysroot (``rpi-sysroot``),
* The toolchain cmake file (``toolchain-aarch64.cmake``),
* The ``pyside-setup`` repository,

An example of the ``setup.py`` invocation might look like the following:

.. code-block:: bash

    python setup.py bdist_wheel \
        --parallel=8 --ignore-git --reuse-build --standalone --limited-api=yes \
        --cmake-toolchain-file=/opt/toolchain-aarch64.cmake \
        --qt-host-path=/opt/Qt/6.3.0/gcc_64 \
        --plat-name=linux_aarch64 \

Depending on the target platform, you could use ``linux_armv7``,
``linux_aarch64``, etc.

If the process succeeds, you will find the target wheels in your ``dist/``
directory, for example:

.. code-block:: bash

    PySide6-6.3.0-6.3.0-cp36-abi3-manylinux2014_aarch64.whl
    shiboken6-6.3.0-6.3.0-cp36-abi3-manylinux2014_aarch64.whl


Troubleshooting
***************

* If the auto-detection mechanism fails to find the Python or Qt installations
  you have in your target device, you can use two additional options::

      --python-target-path=...

  and::

      --qt-target-path=...

* In case the automatic build of the host Shiboken (generator) fails,
  you can specify the custom path using::

      --shiboken-host-path=...

.. _`Manjaro ARM`: https://manjaro.org/download/#ARM
.. _`Archlinux ARM`: https://archlinuxarm.org
.. _`ARM Developer Cross Compilers`: https://developer.arm.com/tools-and-software/open-source-software/developer-tools/gnu-toolchain/gnu-a/downloads
.. _`gcc-arm-10.2-2020.11-x86_64-aarch64-none-linux-gnu.tar.xz`: https://developer.arm.com/-/media/Files/downloads/gnu-a/10.2-2020.11/binrel/gcc-arm-10.2-2020.11-x86_64-aarch64-none-linux-gnu.tar.xz

.. _building_documentation:

Building the documentation
--------------------------

Starting from 5.15, there are two options to build the documentation:

1. Building rst-only documentation (no API)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The process of parsing Qt headers to generate the PySide API documentation can take several
minutes, this means that modifying a specific section of the rst files we currently have, might
become a hard task.

For this, you can install :command:`sphinx` on a virtual environment, and execute the following command::

    python setup.py build_rst_docs

which will generate a ``html/`` directory with the following structure::

    html
    └── pyside6
        ├── index.html
        ├── ...
        └── shiboken6
            ├── index.html
            └── ...

so you can open the main page ``html/pyside6/index.html`` on your browser to check the generated
files.

This is useful when updating the general sections of the documentation, adding tutorials,
modifying the build instructions, and more.

2. Building the documentation (rst + API)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The documentation is being generated using **qdoc** to get the API information, and also **sphinx**
for the local Python related notes.

The system required ``libxml2`` and ``libxslt``, also on the Python environment, ``sphinx`` and
``graphviz`` need to be installed before running the installation process::

    pip install graphviz sphinx sphinx_tabs

After installing ``graphviz``, the ``dot`` command needs to be in PATH, otherwise,
the process will fail. Installing ``graphviz`` system-wide is also an option.

Since the process relies on a Qt installation, you need to specify where the
``qtbase`` directory is located::

    export QT_SRC_DIR=/path/to/qtbase

Once the build process finishes, you can go to the generated ``*_build/*_release/pyside6``
directory, and run::

    ninja apidoc

.. note:: The :command:`apidoc` make target builds offline documentation in QCH (Qt Creator Help)
   format by default. You can switch to building for the online use with the ``--doc-build-online``
   configure option.

The target executes several steps:

#. The ``qdoc`` tool is run over the Qt source code to produce documentation in WebXML format.
#. ``shiboken6`` is run to extract the functions for which bindings exist from WebXML and convert it into RST.
#. ``sphinx`` is run to produce the documentation in HTML format.

Re-running the command will not execute step 1 unless the file
``qdoc_output/webxml/qtcore-index.webxml`` is removed from the build tree.
Similarly, step 2 will not be executed unless the file ``rst/PySide6/QtCore/index.rst``
is removed.

Finally, you will get a ``html`` directory containing all the generated documentation. The offline
help files, ``PySide.qch`` and ``Shiboken.qch``, can be moved to any directory of your choice. You
can find ``Shiboken.qch`` in the build directory, ``*_build\*_release\shiboken6\doc\html``.

If you want to temporarily change a ``.rst`` file to examine the impact on
formatting, you can re-run ``sphinx`` in the ``doc`` directory::

    sphinx-build rst html

Viewing offline documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The offline documentation (QCH) can be viewed using the Qt Creator IDE or Qt Assistant, which is
a standalone application for viewing QCH files.

To view the QCH using Qt Creator, following the instructions outlined in
`Using Qt Creator Help Mode <https://doc.qt.io/qtcreator/creator-help.html>`_. If you chose to
use Qt Assistant instead, use the following command to register the QCH file before launching
Qt Assistant::

    assistant -register PySide.qch

.. note:: Qt Assistant renders the QCH content using the QTextBrowser backend, which supports
   a subset of the CSS styles, However, Qt Creator offers an alternative litehtml-based
   backend, which offers better browsing experience. At the moment, this is not the default
   backend, so you have to select the litehtml backend
   explicitly under the ``General`` tab in ``Qt Creator >> Tools >> Options >> Help``.

Using the internal tools
------------------------

A set of tools can be found under the ``tools/`` directory inside the ``pyside-setup`` repository.

* ``checklibs.py``: Script to analyze dynamic library dependencies of Mach-O binaries.
  To use this utility, just run::

    python checklibs.py /path/to/some.app/Contents/MacOS/Some

  This script was fetched from this repository_.

* ``create_changelog.py``: Script used to create the CHANGELOG that you can find in the ``dist/``
  directory. Usage::

    python create_changelog.py -r 6.0.1 -v v6.0.0..6.0 -t bug-fix

* ``debug_windows.py``: This script can be used to find out why PySide modules
  fail to load with various DLL errors like Missing DLL or Missing symbol in DLL.

  You can think of it as a Windows version of :command:`ldd` / ``LD_DEBUG``.

  Underneath, it uses the :command:`cdb.exe` command line debugger and the :command:`gflags.exe`
  tool, which are installed with the latest Windows Kit.

  The aim is to help developers debug issues that they may encounter using the PySide imports on
  Windows. The user should then provide the generated log file.

  Incidentally it can also be used for any Windows executables, not just Python.
  To use it just run::

    python debug_windows.py

* ``missing_bindings.py``: This script is used to compare the state of PySide and PyQt
  regarding available modules and classses. This content is displayed in our `wiki page`_,
  and can be used as follows::

    python missing_bindings.py --qt-version 6.0.1 -w all

.. note:: The script relies on BeautifulSoup to parse the content and generate a list of the
   missing bindings.

.. _repository: https://github.com/liyanage/macosx-shell-scripts/
.. _`wiki page`: https://wiki.qt.io/Qt_for_Python_Missing_Bindings
.. _BeautifulSoup: https://www.crummy.com/software/BeautifulSoup/
