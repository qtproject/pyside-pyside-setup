How To Debug a C++ Extension of a PySide6 Application?
******************************************************

When debugging PySide code, very often you would also like to debug the
corresponding C++ extension of the PySide module. This is done by attaching your
debugger to the Python interpreter. In this tutorial, we are going to take you
through a comprehensive guide in building Qt 6, using the built Qt 6 to build
PySide6, and then starting a debugging process in either Qt Creator or VSCode.

With VSCode, you should be able to see the combined call stacks for both C++ and
Python together. With Qt Creator, unfortunately you would only be able to
debug the native C++ code of the PySide module; that is you won't be able to set
breakpoints inside the Python code.

.. note:: This tutorial is created on Ubuntu 20.04 LTS with the debugger as GDB.
          As such, this tutorial is mainly focused on Linux users. Nevertheless, links to
          setup everything in other platforms are mentioned along with each
          sub-section.

Let's get started.

Install All The Library Dependencies Based on Your Platform
-----------------------------------------------------------

.. code-block:: bash

    sudo apt install libfontconfig1-dev libfreetype6-dev \
    libx11-dev libx11-xcb-dev libxext-dev libxfixes-dev \
    libxi-dev libxrender-dev libxcb1-dev libxcb-glx0-dev \
    libxcb-keysyms1-dev libxcb-image0-dev libxcb-shm0-dev \
    libxcb-icccm4-dev libxcb-sync-dev libxcb-xfixes0-dev \
    libxcb-shape0-dev libxcb-randr0-dev libxcb-render-util0-dev \
    libxcb-util-dev libxcb-xinerama0-dev libxcb-xkb-dev \
    libxkbcommon-dev libxkbcommon-x11-dev libatspi2.0-dev \
    libopengl0 -y

If you have to use the Qt Multimedia module, you have to install gstreamer also.

.. code-block:: bash

    sudo apt-get install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
    libgstreamer-plugins-bad1.0-dev gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-doc \
    gstreamer1.0-tools gstreamer1.0-x gstreamer1.0-alsa gstreamer1.0-gl \
    gstreamer1.0-gtk3 gstreamer1.0-qt5 gstreamer1.0-pulseaudio

Generally, any information on missing packages can be found by inspecting the
config.summary in you CMake build folder.

.. note:: For other platforms install the same packages using the instructions
          mentioned here `Qt Install on Linux <https://doc.qt.io/qt-6/linux-requirements.html>`_

Build Qt
--------

This is an optional step in case you only want to debug the CPython bindings or if you have DEBUG_SYMBOLS for Qt 6 already.

There are multiple ways to build Qt - configure script or manually with CMake.
Find the build system information `Qt 6 Build System
<https://www.qt.io/blog/qt-6-build-system>`_.

1. Get the source code.

   .. code-block:: bash

      git clone git://code.qt.io/qt/qt5.git
      # Get submodules
      cd qt5
      perl init-repository

2. Once you have the source code, the next step is to generate the build using
   CMake, then building and installing it.

   .. code-block:: bash

      cmake -GNinja -DMCAKE_BUILD_TYPE=Debug \
      -DCMAKE_INSTALL_PREFIX=/path/to/install/Qt -DBUILD_qtwebengine=OFF ..
      cmake --build . --parallel
      cmake --install .

   As you notice here, we are skipping the Qt WebEngine module because this greatly
   decreases the build time. However, PySide6 supports Qt WebEngine
   features. So feel free to add it, if you need it.

More instructions on building Qt 6 can be found in the following links:

* https://wiki.qt.io/Building_Qt_6_from_Git
* https://code.qt.io/cgit/qt/qtbase.git/tree/cmake/README.md
* https://code.qt.io/cgit/qt/qtbase.git/tree/cmake/configure-cmake-mapping.md

Add the **bin** and **lib** path to the environment variables
--------------------------------------------------------------

.. code-block:: bash

    export PATH="/path/to/custom/qt/bin:$PATH"
    export LD_LIBRARY_PATH="/path/to/custom/qt/lib:$LD_LIBRARY_PATH"

Build PySide6 using the Qt 6 that you built earlier
----------------------------------------------------

Follow the steps mentioned `Getting Started - Qt for Python
<https://doc.qt.io/qtforpython/gettingstarted.html>`_

You may manually select the modules to install using the ``--module-subset`` cli
argument for `setup.py`. This was my installation script

.. code-block:: bash

    python setup.py install --qpaths=/path/to/qpaths --debug \
    --ignore-git --reuse-build

It is recommended to use a Python virtual environment rather than installing in the global Python.

Debugging the process using your preferred IDE
----------------------------------------------

The following sections guide you through the setup for Qt Creator or VSCode.

.. toctree::
   :glob:
   :titlesonly:

   qtcreator/qtcreator
   vscode/vscode
