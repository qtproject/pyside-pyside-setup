# PySide6

### Introduction

**Important:** for Qt5 compatibility, check [PySide2](https://pypi.org/project/PySide2)

PySide6 is the official Python module from the
[Qt for Python project](https://wiki.qt.io/Qt_for_Python),
which provides access to the complete Qt 6.0+ framework.

The Qt for Python project is developed in the open, with all facilities you'd expect
from any modern OSS project such as all code in a git repository and an open
design process. We welcome any contribution conforming to the
[Qt Contribution Agreement](https://www.qt.io/contributionagreement/).

### Installation

Since the release of the [Technical Preview](https://blog.qt.io/blog/2018/06/13/qt-python-5-11-released/)
it is possible to install via `pip`, both from Qt's servers
and [PyPi](https://pypi.org/project/PySide6/):

```
pip install PySide6
```

#### Dependencies

PySide6 versions following 6.0 use a C++ parser based on
[Clang](http://clang.org/). The Clang library (C-bindings), version 10.0 or
higher is required for building. Prebuilt versions of it can be downloaded from
[download.qt.io](https://download.qt.io/development_releases/prebuilt/libclang/).

After unpacking the archive, set the environment variable *LLVM_INSTALL_DIR* to
point to the folder containing the *include* and *lib* directories of Clang:

```
7z x .../libclang-release_100-linux-Rhel7.2-gcc5.3-x86_64-clazy.7z
export LLVM_INSTALL_DIR=$PWD/libclang
```

On Windows:

```
7z x .../libclang-release_100-windows-vs2015_64-clazy.7z
SET LLVM_INSTALL_DIR=%CD%\libclang
```

### Building from source

For building PySide6 from scratch, please read about
[getting started](https://doc.qt.io/qtforpython/gettingstarted.html).
This process will include getting the code:

```
git clone https://code.qt.io/pyside/pyside-setup
cd pyside-setup
git checkout 6.x # if a specific version is needed
```

then install the dependencies, and following the instructions per platform.
A common build command will look like:

```
python setup.py install --qmake=/path/to/bin/qmake --parallel=8 --build-tests
```

You can obtain more information about the options to build PySide and Shiboken
in [our wiki](https://wiki.qt.io/Qt_for_Python/).

### Documentation and Bugs

You can find more information about the PySide6 module API in the
[official Qt for Python documentation](https://doc.qt.io/qtforpython/).

If you come across any issue, please file a bug report at our
[JIRA tracker](https://bugreports.qt.io/projects/PYSIDE) following
our [guidelines](https://wiki.qt.io/Qt_for_Python/Reporting_Bugs).

### Community

Check *#qt-pyside*, our official IRC channel on FreeNode, or contact us via our
[mailing list](https://lists.qt-project.org/mailman/listinfo/pyside).

### Licensing

PySide6 is available under both Open Source (LGPLv3/GPLv2) and commercial
license.  Using PyPi is the recommended installation source, because the
content of the wheels is valid for both cases.  For more information, refer to
the [Qt Licensing page](https://www.qt.io/licensing/).
