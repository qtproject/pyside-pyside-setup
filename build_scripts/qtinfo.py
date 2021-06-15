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
            self._qmake_command = None
            # Dict to cache qmake values.
            self._query_dict = {}
            # Dict to cache mkspecs variables.
            self._mkspecs_dict = {}

        def setup(self, qmake):
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

        def get_mkspecs_variables(self):
            return self._mkspecs_dict

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

        def _parse_qt_build_type(self):
            key = "QT_CONFIG"
            if key not in self._mkspecs_dict:
                return None

            qt_config = self._mkspecs_dict[key]
            if "debug_and_release" in qt_config:
                return "debug_and_release"

            split = qt_config.split(" ")
            if "release" in split and "debug" in split:
                return "debug_and_release"

            if "release" in split:
                return "release"

            if "debug" in split:
                return "debug"

            return None

        def _get_other_properties(self):
            # Get the src property separately, because it is not returned by
            # qmake unless explicitly specified.
            key = "QT_INSTALL_PREFIX/src"
            result = self._get_qmake_output(["-query", key])
            self._query_dict[key] = result

            # Get mkspecs variables and cache them.
            self._get_qmake_mkspecs_variables()

            # Get macOS minimum deployment target.
            key = "QMAKE_MACOSX_DEPLOYMENT_TARGET"
            if key in self._mkspecs_dict:
                self._query_dict[key] = self._mkspecs_dict[key]

            # Figure out how Qt was built:
            #   debug mode, release mode, or both.
            build_type = self._parse_qt_build_type()
            if build_type:
                self._query_dict["BUILD_TYPE"] = build_type

        def _get_qmake_mkspecs_variables(self):
            # Create an empty qmake project file in a temporary directory
            # where also the .qmake.stash file will be created.
            lines = []
            with tempfile.TemporaryDirectory() as tempdir:
                pro_file = Path(tempdir) / 'project.pro'
                pro_file.write_text('')
                # Query qmake for all of its mkspecs variables.
                args = ["-E", os.fspath(pro_file)]
                qmake_output = self._get_qmake_output(args, cwd=tempdir)
                lines = [s.strip() for s in qmake_output.splitlines()]

            if not lines:
                raise RuntimeError("Could not determine qmake variables")

            pattern = re.compile(r"^(.+?)=(.+?)$")
            for line in lines:
                found = pattern.search(line)
                if found:
                    key = found.group(1).strip()
                    value = found.group(2).strip()
                    self._mkspecs_dict[key] = value
