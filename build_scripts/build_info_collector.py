#############################################################################
##
## Copyright (C) 2021 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of Qt for Python.
##
## $QT_BEGIN_LICENSE:LGPL$
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
##
## GNU Lesser General Public License Usage
## Alternatively, this file may be used under the terms of the GNU Lesser
## General Public License version 3 as published by the Free Software
## Foundation and appearing in the file LICENSE.LGPL3 included in the
## packaging of this file. Please review the following information to
## ensure the GNU Lesser General Public License version 3 requirements
## will be met: https://www.gnu.org/licenses/lgpl-3.0.html.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU
## General Public License version 2.0 or (at your option) the GNU General
## Public license version 3 or any later version approved by the KDE Free
## Qt Foundation. The licenses are as published by the Free Software
## Foundation and appearing in the file LICENSE.GPL2 and LICENSE.GPL3
## included in the packaging of this file. Please review the following
## information to ensure the GNU General Public License requirements will
## be met: https://www.gnu.org/licenses/gpl-2.0.html and
## https://www.gnu.org/licenses/gpl-3.0.html.
##
## $QT_END_LICENSE$
##
#############################################################################

import os
import platform
import sys

from setuptools._distutils import log
from setuptools._distutils.errors import DistutilsSetupError
from sysconfig import get_config_var
from setuptools._distutils import sysconfig as sconfig

from .options import OPTION
from .qtinfo import QtInfo
from .wheel_utils import get_qt_version


# Return a prefix suitable for the _install/_build directory
def prefix():
    virtual_env_name = os.environ.get('VIRTUAL_ENV', None)
    if virtual_env_name is not None:
        name = os.path.basename(virtual_env_name)
    else:
        name = "pyside"
    name += str(sys.version_info[0])
    if OPTION["DEBUG"]:
        name += "d"
    if is_debug_python():
        name += "p"
    if OPTION["LIMITED_API"] == "yes":
        name += "a"
    return name


def is_debug_python():
    return getattr(sys, "gettotalrefcount", None) is not None


def _get_py_library_win(build_type, py_version, py_prefix, py_libdir,
                        py_include_dir):
    """Helper for finding the Python library on Windows"""
    if py_include_dir is None or not os.path.exists(py_include_dir):
        py_include_dir = os.path.join(py_prefix, "include")
    if py_libdir is None or not os.path.exists(py_libdir):
        # For virtual environments on Windows, the py_prefix will contain a
        # path pointing to it, instead of the system Python installation path.
        # Since INCLUDEPY contains a path to the system location, we use the
        # same base directory to define the py_libdir variable.
        py_libdir = os.path.join(os.path.dirname(py_include_dir), "libs")
        if not os.path.isdir(py_libdir):
            raise DistutilsSetupError("Failed to locate the 'libs' directory")
    dbg_postfix = "_d" if build_type == "Debug" else ""
    if OPTION["MAKESPEC"] == "mingw":
        static_lib_name = f"libpython{py_version.replace('.', '')}{dbg_postfix}.a"
        return os.path.join(py_libdir, static_lib_name)
    v = py_version.replace(".", "")
    python_lib_name = f"python{v}{dbg_postfix}.lib"
    return os.path.join(py_libdir, python_lib_name)


def _get_py_library_unix(build_type, py_version, py_prefix, py_libdir,
                         py_include_dir):
    """Helper for finding the Python library on UNIX"""
    if py_libdir is None or not os.path.exists(py_libdir):
        py_libdir = os.path.join(py_prefix, "lib")
    if py_include_dir is None or not os.path.exists(py_include_dir):
        dir = f"include/python{py_version}"
        py_include_dir = os.path.join(py_prefix, dir)
    dbg_postfix = "_d" if build_type == "Debug" else ""
    lib_exts = ['.so']
    if sys.platform == 'darwin':
        lib_exts.append('.dylib')
    lib_suff = getattr(sys, 'abiflags', None)
    lib_exts.append('.so.1')
    # Suffix for OpenSuSE 13.01
    lib_exts.append('.so.1.0')
    # static library as last gasp
    lib_exts.append('.a')

    libs_tried = []
    for lib_ext in lib_exts:
        lib_name = f"libpython{py_version}{lib_suff}{lib_ext}"
        py_library = os.path.join(py_libdir, lib_name)
        if os.path.exists(py_library):
            return py_library
        libs_tried.append(py_library)

    # Try to find shared libraries which have a multi arch
    # suffix.
    py_multiarch = get_config_var("MULTIARCH")
    if py_multiarch:
        try_py_libdir = os.path.join(py_libdir, py_multiarch)
        libs_tried = []
        for lib_ext in lib_exts:
            lib_name = f"libpython{py_version}{lib_suff}{lib_ext}"
            py_library = os.path.join(try_py_libdir, lib_name)
            if os.path.exists(py_library):
                return py_library
            libs_tried.append(py_library)

    raise DistutilsSetupError(f"Failed to locate the Python library with {', '.join(libs_tried)}")


def get_py_library(build_type, py_version, py_prefix, py_libdir, py_include_dir):
    """Find the Python library"""
    if sys.platform == "win32":
        py_library = _get_py_library_win(build_type, py_version, py_prefix,
                                         py_libdir, py_include_dir)
    else:
        py_library = _get_py_library_unix(build_type, py_version, py_prefix,
                                          py_libdir, py_include_dir)
    if py_library.endswith('.a'):
        # Python was compiled as a static library
        log.error(f"Failed to locate a dynamic Python library, using {py_library}")
    return py_library


class BuildInfoCollectorMixin(object):
    build_base: str
    build_lib: str
    cmake: str
    cmake_toolchain_file: str
    is_cross_compile: bool
    plat_name: str
    python_target_path: str

    def __init__(self):
        pass

    def collect_and_assign(self):
        script_dir = os.getcwd()

        # build_base is not set during install command, so we default to
        # the 'build command's build_base value ourselves.
        build_base = self.build_base
        if not build_base:
            self.build_base = "build"
            build_base = self.build_base

        sources_dir = os.path.join(script_dir, "sources")

        platform_arch = platform.architecture()[0]
        log.info(f"Python architecture is {platform_arch}")
        self.py_arch = platform_arch[:-3]

        build_type = "Debug" if OPTION["DEBUG"] else "Release"
        if OPTION["RELWITHDEBINFO"]:
            build_type = 'RelWithDebInfo'

        # Prepare parameters
        py_executable = sys.executable
        py_version = f"{sys.version_info[0]}.{sys.version_info[1]}"
        py_include_dir = get_config_var("INCLUDEPY")
        py_libdir = get_config_var("LIBDIR")
        # distutils.sysconfig.get_config_var('prefix') returned the
        # virtual environment base directory, but
        # sysconfig.get_config_var returns the system's prefix.
        # We use 'base' instead (although, platbase points to the
        # same location)
        py_prefix = get_config_var("base")
        if not py_prefix or not os.path.exists(py_prefix):
            py_prefix = sys.prefix
        self.py_prefix = py_prefix
        if sys.platform == "win32":
            py_scripts_dir = os.path.join(py_prefix, "Scripts")
        else:
            py_scripts_dir = os.path.join(py_prefix, "bin")
        self.py_scripts_dir = py_scripts_dir

        self.qtinfo = QtInfo()
        qt_version = get_qt_version()

        # Used for test blacklists and registry test.
        self.build_classifiers = (f"py{py_version}-qt{qt_version}-{platform.architecture()[0]}-"
                                  f"{build_type.lower()}")

        if OPTION["SHORTER_PATHS"]:
            build_name = f"p{py_version}"
        else:
            build_name = self.build_classifiers

        build_dir = os.path.join(script_dir, f"{prefix()}_build", f"{build_name}")
        install_dir = os.path.join(script_dir, f"{prefix()}_install", f"{build_name}")

        self.script_dir = script_dir
        self.sources_dir = sources_dir
        self.build_dir = build_dir
        self.install_dir = install_dir
        self.py_executable = py_executable
        self.py_include_dir = py_include_dir
        self.py_library = get_py_library(build_type, py_version, py_prefix,
                                         py_libdir, py_include_dir)
        self.py_version = py_version
        self.build_type = build_type
        self.site_packages_dir = sconfig.get_python_lib(1, 0, prefix=install_dir)

    def post_collect_and_assign(self):
        # self.build_lib is only available after the base class
        # finalize_options is called.
        self.st_build_dir = os.path.join(self.script_dir, self.build_lib)
