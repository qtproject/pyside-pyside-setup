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

It is possible to install via `pip`, both from Qt's servers
and [PyPi](https://pypi.org/project/PySide6/):

```
pip install PySide6
```

> Please note: this wheel is an alias to other two wheels
> [PySide6_Essentials](https://pypi.org/project/PySide6_Essentials) and
> [PySide6_Addons](https://pypi.org/project/PySide6_Addons), which contains
> a predefined list of Qt Modules.

#### Dependencies

PySide6 versions following 6.0 use a C++ parser based on
[Clang](https://clang.llvm.org/). The Clang library (C-bindings),
is required for building. Prebuilt versions of it can be downloaded from
[download.qt.io](https://download.qt.io/development_releases/prebuilt/libclang/).

After unpacking the archive, set the environment variable *LLVM_INSTALL_DIR* to
point to the folder containing the *include* and *lib* directories of Clang:

```
7z x .../libclang-release_22.1.8-based-linux-Rhel9.6-gcc11.4-x86_64.7z
export LLVM_INSTALL_DIR=$PWD/libclang
```

On Windows:

```
7z x .../libclang-release_22.1.8-based-windows-vs2022_64.7z
SET LLVM_INSTALL_DIR=%CD%\libclang
```

### Building from source

For building PySide6 from scratch, please read about
[Building from Source](https://doc.qt.io/qtforpython-6/building_from_source/index.html).
This process will include getting the code:

```
git clone https://code.qt.io/pyside/pyside-setup
cd pyside-setup
git checkout 6.x # if a specific version is needed
```

then install the dependencies, and following the instructions per platform.
A common build command will look like:

```
python setup.py install --qtpaths=/path/to/bin/qtpaths6 --build-tests
```

You can obtain more information about the options to build PySide and Shiboken
in [our wiki](https://wiki.qt.io/Qt_for_Python).

### Documentation and Bugs

You can find more information about the PySide6 module API in the
[official Qt for Python documentation](https://doc.qt.io/qtforpython/).

If you come across any issue, please file a bug report at our
[JIRA tracker](https://qt-project.atlassian.net/browse/PYSIDE) following
our [guidelines](https://wiki.qt.io/Qt_for_Python/Reporting_Bugs).

### Community

Check our channels on IRC (Libera), Telegram, Gitter, Matrix, and mailing list,
and [join our community](https://wiki.qt.io/Qt_for_Python#Community)!

### Licensing

PySide6 is available under both Open Source (LGPLv3 or GPLv2 or GPLv3) and commercial
license. Using PyPi is the recommended installation source, because the
content of the wheels is valid for both cases. For more information, refer to
the [Qt Licensing page](https://www.qt.io/licensing/).
