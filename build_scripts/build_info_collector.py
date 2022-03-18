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
from .utils import configure_cmake_project, parse_cmake_project_message_info
from .wheel_utils import get_qt_version


# Return a prefix suitable for the _install/_build directory
def prefix():
    virtual_env_name = os.environ.get('VIRTUAL_ENV', None)
    has_virtual_env = False
    if virtual_env_name is not None:
        name = os.path.basename(virtual_env_name)
        has_virtual_env = True
    else:
        name = "qfp"
    if OPTION["DEBUG"]:
        name += "d"
    if is_debug_python():
        name += "p"
    if OPTION["LIMITED_API"] == "yes":
        name += "a"
    return name, has_virtual_env


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

    # PYSIDE-535: See if this is PyPy.
    if hasattr(sys, "pypy_version_info"):
        pypy_libdir = os.path.join(os.path.dirname(py_libdir), "bin")
        for lib_ext in lib_exts:
            lib_name = f"libpypy3-c{lib_ext}"
            pypy_library = os.path.join(pypy_libdir, lib_name)
            if os.path.exists(pypy_library):
                return pypy_library
            libs_tried.append(pypy_library)
    _libs_tried = ', '.join(libs_tried)
    raise DistutilsSetupError(f"Failed to locate the Python library with {_libs_tried}")


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
    internal_cmake_install_dir_query_file_path: str
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

        if self.is_cross_compile:
            config_tests_dir = os.path.join(script_dir, build_base, "config.tests")
            python_target_info_dir = os.path.join(sources_dir, "shiboken6", "config.tests",
                                                  "target_python_info")
            cmake_cache_args = []

            if self.python_target_path:
                cmake_cache_args.append(("Python_ROOT_DIR", self.python_target_path))

            if self.cmake_toolchain_file:
                cmake_cache_args.append(("CMAKE_TOOLCHAIN_FILE", self.cmake_toolchain_file))
            python_target_info_output = configure_cmake_project(
                python_target_info_dir,
                self.cmake,
                temp_prefix_build_path=config_tests_dir,
                cmake_cache_args=cmake_cache_args)
            python_target_info = parse_cmake_project_message_info(python_target_info_output)
            self.python_target_info = python_target_info

        build_type = "Debug" if OPTION["DEBUG"] else "Release"
        if OPTION["RELWITHDEBINFO"]:
            build_type = 'RelWithDebInfo'

        # Prepare parameters
        if not self.is_cross_compile:
            platform_arch = platform.architecture()[0]
            self.py_arch = platform_arch[:-3]

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
        else:
            # We don't look for an interpreter when cross-compiling.
            py_executable = None

            python_info = self.python_target_info['python_info']
            py_version = python_info['version'].split('.')
            py_version = f"{py_version[0]}.{py_version[1]}"
            py_include_dir = python_info['include_dirs']
            py_libdir = python_info['library_dirs']
            py_library = python_info['libraries']
            self.py_library = py_library

            # Prefix might not be set because the project that extracts
            # the info is using internal API to get it. It shouldn't be
            # critical though, because we don't really use neither
            # py_prefix nor py_scripts_dir in important places
            # when cross-compiling.
            if 'prefix' in python_info:
                py_prefix = python_info['prefix']
                self.py_prefix = py_prefix

                py_scripts_dir = os.path.join(py_prefix, 'bin')
                if os.path.exists(py_scripts_dir):
                    self.py_scripts_dir = py_scripts_dir
                else:
                    self.py_scripts_dir = None
            else:
                py_prefix = None
                self.py_prefix = py_prefix
                self.py_scripts_dir = None

        self.qtinfo = QtInfo()
        qt_version = get_qt_version()

        # Used for test blacklists and registry test.
        if self.is_cross_compile:
            # Querying the host platform architecture makes no sense when cross-compiling.
            build_classifiers = f"py{py_version}-qt{qt_version}-{self.plat_name}-"
        else:
            build_classifiers = f"py{py_version}-qt{qt_version}-{platform.architecture()[0]}-"
            if hasattr(sys, "pypy_version_info"):
                pypy_version = ".".join(map(str, sys.pypy_version_info[:3]))
                build_classifiers += f"pypy.{pypy_version}-"
        build_classifiers += f"{build_type.lower()}"
        self.build_classifiers = build_classifiers

        venv_prefix, has_virtual_env = prefix()

        # The virtualenv name serves as the base of the build dir
        # and we consider it is distinct enough that we don't have to
        # append the build classifiers, thus keeping dir names shorter.
        build_name = f"{venv_prefix}"
        if self.is_cross_compile and has_virtual_env:
            build_name += f"-{self.plat_name}"

        # If short paths are requested and no virtual env is found, at
        # least append the python version for more uniqueness.
        if OPTION["SHORTER_PATHS"] and not has_virtual_env:
            build_name += f"-p{py_version}"
        # If no virtual env is found, use build classifiers for
        # uniqueness.
        elif not has_virtual_env:
            build_name += f"-{self.build_classifiers}"

        common_prefix_dir = os.path.join(script_dir, build_base)
        build_dir = os.path.join(common_prefix_dir, build_name, "build")
        install_dir = os.path.join(common_prefix_dir, build_name, "install")

        # Change the setuptools build_lib dir to be under the same
        # directory where the cmake build and install dirs are so
        # there's a common subdirectory for all build-related dirs.
        # Example:
        # Replaces
        #   build/lib.macosx-10.14-x86_64-3.7' with
        #   build/{venv_prefix}/package'
        setup_tools_build_lib_dir = os.path.join(common_prefix_dir, build_name, "package")
        self.build_lib = setup_tools_build_lib_dir

        self.script_dir = script_dir
        self.sources_dir = sources_dir
        self.build_dir = build_dir
        self.install_dir = install_dir
        self.py_executable = py_executable
        self.py_include_dir = py_include_dir

        if not self.is_cross_compile:
            self.py_library = get_py_library(build_type, py_version, py_prefix,
                                             py_libdir, py_include_dir)
        self.py_version = py_version
        self.build_type = build_type

        if self.is_cross_compile:
            site_packages_without_prefix = self.python_target_info['python_info']['site_packages_dir']
            self.site_packages_dir = os.path.join(install_dir, site_packages_without_prefix)
        else:
            self.site_packages_dir = sconfig.get_python_lib(1, 0, prefix=install_dir)

    def post_collect_and_assign(self):
        # self.build_lib is only available after the base class
        # finalize_options is called.
        self.st_build_dir = os.path.join(self.script_dir, self.build_lib)
