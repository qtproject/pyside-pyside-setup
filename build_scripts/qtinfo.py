#############################################################################
##
## Copyright (C) 2018 The Qt Company Ltd.
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
import sys
import re
import subprocess
import tempfile
from pathlib import Path


_CMAKE_LISTS = """cmake_minimum_required(VERSION 3.18)
project(dummy LANGUAGES CXX)

find_package(Qt6 COMPONENTS Core)

get_target_property(darwin_target Qt6::Core QT_DARWIN_MIN_DEPLOYMENT_TARGET)
message(STATUS "mkspec_qt_darwin_min_deployment_target=${darwin_target}")

if(QT_FEATURE_debug_and_release)
    message(STATUS "mkspec_build_type=debug_and_release")
elseif(QT_FEATURE_debug)
    message(STATUS "mkspec_build_type=debug")
else()
    message(STATUS "mkspec_build_type=release")
endif()
"""


class QtInfo(object):
    _instance = None  # singleton helpers

    def __new__(cls):  # __new__ always a classmethod
        if not QtInfo._instance:
            QtInfo._instance = QtInfo.__QtInfo()
        return QtInfo._instance

    def __getattr__(self, name):
        return getattr(self._instance, name)

    def __setattr__(self, name):
        return setattr(self._instance, name)

    class __QtInfo:  # Python singleton
        def __init__(self):
            self._cmake_command = None
            self._qmake_command = None
            # Dict to cache qmake values.
            self._query_dict = {}

        def setup(self, cmake, qmake):
            self._cmake_command = cmake
            self._qmake_command = qmake

        @property
        def qmake_command(self):
            qmake_command_string = self._qmake_command[0]
            for entry in self._qmake_command[1:]:
                qmake_command_string = f"{qmake_command_string} {entry}"
            return qmake_command_string

        @property
        def version(self):
            return self.get_property("QT_VERSION")

        @property
        def bins_dir(self):
            return self.get_property("QT_INSTALL_BINS")

        @property
        def libs_dir(self):
            return self.get_property("QT_INSTALL_LIBS")

        @property
        def lib_execs_dir(self):
            return self.get_property("QT_INSTALL_LIBEXECS")

        @property
        def plugins_dir(self):
            return self.get_property("QT_INSTALL_PLUGINS")

        @property
        def prefix_dir(self):
            return self.get_property("QT_INSTALL_PREFIX")

        @property
        def imports_dir(self):
            return self.get_property("QT_INSTALL_IMPORTS")

        @property
        def translations_dir(self):
            return self.get_property("QT_INSTALL_TRANSLATIONS")

        @property
        def headers_dir(self):
            return self.get_property("QT_INSTALL_HEADERS")

        @property
        def docs_dir(self):
            return self.get_property("QT_INSTALL_DOCS")

        @property
        def qml_dir(self):
            return self.get_property("QT_INSTALL_QML")

        @property
        def macos_min_deployment_target(self):
            """ Return value is a macOS version or None. """
            return self.get_property("QMAKE_MACOSX_DEPLOYMENT_TARGET")

        @property
        def build_type(self):
            """
            Return value is either debug, release, debug_release, or None.
            """
            return self.get_property("BUILD_TYPE")

        @property
        def src_dir(self):
            """ Return path to Qt src dir or None.. """
            return self.get_property("QT_INSTALL_PREFIX/src")

        def get_property(self, prop_name):
            if not self._query_dict:
                self._get_query_properties()
                self._get_other_properties()
            if prop_name not in self._query_dict:
                return None
            return self._query_dict[prop_name]

        def _get_qmake_output(self, args_list=[], cwd=None):
            assert self._qmake_command
            cmd = [self._qmake_command]
            cmd.extend(args_list)
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=False,
                                    cwd=cwd)
            output = proc.communicate()[0]
            proc.wait()
            if proc.returncode != 0:
                return ""
            output = str(output, "ascii").strip()
            return output

        def _parse_query_properties(self, process_output):
            props = {}
            if not process_output:
                return props
            lines = [s.strip() for s in process_output.splitlines()]
            for line in lines:
                if line and (":" in line):
                    key, value = line.split(":", 1)
                    props[key] = value
            return props

        def _get_query_properties(self):
            output = self._get_qmake_output(["-query"])
            self._query_dict = self._parse_query_properties(output)

        def _get_other_properties(self):
            # Get the src property separately, because it is not returned by
            # qmake unless explicitly specified.
            key = "QT_INSTALL_PREFIX/src"
            result = self._get_qmake_output(["-query", key])
            self._query_dict[key] = result

            # Get mkspecs variables and cache them.
            # FIXME Python 3.9 self._query_dict |= other_dict
            for key, value in self._get_cmake_mkspecs_variables().items():
                self._query_dict[key] = value

        @staticmethod
        def _parse_cmake_mkspecs_variables(output):
            # Helper for _get_cmake_mkspecs_variables(). Parse the output for
            # anything prefixed '-- mkspec_' as created by the message() calls
            # in _CMAKE_LISTS.
            result = {}
            pattern = re.compile(r"^-- mkspec_(.*)=(.*)$")
            for line in output.splitlines():
                found = pattern.search(line.strip())
                if found:
                    key = found.group(1).strip()
                    value = found.group(2).strip()
                    # Get macOS minimum deployment target.
                    if key == 'qt_darwin_min_deployment_target':
                        result['QMAKE_MACOSX_DEPLOYMENT_TARGET'] = value
                    # Figure out how Qt was built
                    elif key == 'build_type':
                        result['BUILD_TYPE'] = value
            return result

        def _get_cmake_mkspecs_variables(self):
            # Create an empty cmake project file in a temporary directory and
            # parse the output to determine some mkspec values.
            output = ''
            error = ''
            return_code = 0
            with tempfile.TemporaryDirectory() as tempdir:
                cmake_list_file = Path(tempdir) / 'CMakeLists.txt'
                cmake_list_file.write_text(_CMAKE_LISTS)
                cmd = [self._cmake_command, '-G', 'Ninja', '.']
                # FIXME Python 3.7: Use subprocess.run()
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=False,
                                        cwd=tempdir, universal_newlines=True)
                output, error = proc.communicate()
                proc.wait()
                return_code = proc.returncode

            if return_code != 0:
                raise RuntimeError(f"Could not determine cmake variables: {error}")
            return QtInfo.__QtInfo._parse_cmake_mkspecs_variables(output)
