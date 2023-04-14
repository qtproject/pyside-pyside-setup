# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import os
import subprocess
from pathlib import Path

from .utils import (configure_cmake_project, parse_cmake_project_message_info,
                    platform_cmake_options)


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
            self._qtpaths_command = None
            self._cmake_command = None
            self._qmake_command = None
            self._force_qmake = False
            self._use_cmake = False
            self._qt_target_path = None
            self._cmake_toolchain_file = None
            # Dict to cache qmake values.
            self._query_dict = {}

        def setup(self, qtpaths, cmake, qmake, force_qmake, use_cmake, qt_target_path,
                  cmake_toolchain_file):
            self._qtpaths_command = qtpaths
            self._cmake_command = cmake
            self._qmake_command = qmake
            self._force_qmake = force_qmake
            self._use_cmake = use_cmake
            self._qt_target_path = qt_target_path
            self._cmake_toolchain_file = cmake_toolchain_file

        @property
        def qmake_command(self):
            return self._qmake_command

        @property
        def qtpaths_command(self):
            return self._qtpaths_command

        @property
        def version(self):
            return self.get_property("QT_VERSION")

        @property
        def version_tuple(self):
            return tuple(map(int, self.version.split(".")))

        @property
        def bins_dir(self):
            return self.get_property("QT_INSTALL_BINS")

        @property
        def data_dir(self):
            return self.get_property("QT_INSTALL_DATA")

        @property
        def libs_dir(self):
            return self.get_property("QT_INSTALL_LIBS")

        @property
        def module_json_files_dir(self):
            install_libs = self.get_property("QT_INSTALL_LIBS")
            result = Path(install_libs).parent / "modules"
            return os.fspath(result)

        @property
        def metatypes_dir(self):
            parent = self.arch_data if self.version_tuple >= (6, 5, 0) else self.libs_dir
            return os.fspath(Path(parent) / "metatypes")

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
        def arch_data(self):
            return self.get_property("QT_INSTALL_ARCHDATA")

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

        def _get_qtpaths_output(self, args_list=None, cwd=None):
            if args_list is None:
                args_list = []
            assert self._qtpaths_command
            cmd = [str(self._qtpaths_command)]
            cmd.extend(args_list)
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=False,
                                    cwd=cwd, universal_newlines=True)
            output, error = proc.communicate()
            proc.wait()
            if proc.returncode != 0:
                raise RuntimeError(f"Could not run {self._qtpaths_command}: {error}")
            return output

        # FIXME PYSIDE7: Remove qmake handling
        def _get_qmake_output(self, args_list=None, cwd=None):
            if args_list is None:
                args_list = []
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
            if self._use_cmake:
                setup_script_dir = Path.cwd()
                sources_dir = setup_script_dir / "sources"
                qt_target_info_dir = sources_dir / "shiboken6" / "config.tests" / "target_qt_info"
                qt_target_info_dir = os.fspath(qt_target_info_dir)
                config_tests_dir = setup_script_dir / "build" / "config.tests"
                config_tests_dir = os.fspath(config_tests_dir)

                cmake_cache_args = []
                if self._cmake_toolchain_file:
                    cmake_cache_args.append(("CMAKE_TOOLCHAIN_FILE", self._cmake_toolchain_file))

                if self._qt_target_path:
                    cmake_cache_args.append(("QFP_QT_TARGET_PATH", self._qt_target_path))
                qt_target_info_output = configure_cmake_project(
                    qt_target_info_dir,
                    self._cmake_command,
                    temp_prefix_build_path=config_tests_dir,
                    cmake_cache_args=cmake_cache_args)
                qt_target_info = parse_cmake_project_message_info(qt_target_info_output)
                self._query_dict = qt_target_info['qt_info']
            else:
                if self._force_qmake:
                    output = self._get_qmake_output(["-query"])
                else:
                    output = self._get_qtpaths_output(["--qt-query"])
                self._query_dict = self._parse_query_properties(output)

        def _get_other_properties(self):
            # Get the src property separately, because it is not returned by
            # qmake unless explicitly specified.
            key = "QT_INSTALL_PREFIX/src"
            if not self._use_cmake:
                if self._force_qmake:
                    result = self._get_qmake_output(["-query", key])
                else:
                    result = self._get_qtpaths_output(["--qt-query", key])
                self._query_dict[key] = result

            # Get mkspecs variables and cache them.
            # FIXME Python 3.9 self._query_dict |= other_dict
            for key, value in self._get_cmake_mkspecs_variables().items():
                self._query_dict[key] = value

        def _get_cmake_mkspecs_variables(self):
            setup_script_dir = Path.cwd()
            sources_dir = setup_script_dir / "sources"
            qt_target_mkspec_dir = sources_dir / "shiboken6" / "config.tests" / "target_qt_mkspec"
            qt_target_mkspec_dir = qt_target_mkspec_dir.as_posix()
            config_tests_dir = setup_script_dir / "build" / "config.tests"
            config_tests_dir = config_tests_dir.as_posix()

            cmake_cache_args = []
            if self._cmake_toolchain_file:
                cmake_cache_args.append(("CMAKE_TOOLCHAIN_FILE", self._cmake_toolchain_file))
                if self._qt_target_path:
                    cmake_cache_args.append(("QFP_QT_TARGET_PATH", self._qt_target_path))
            else:
                qt_prefix = Path(self.prefix_dir).as_posix()
                cmake_cache_args.append(("CMAKE_PREFIX_PATH", qt_prefix))

            cmake_cache_args.extend(platform_cmake_options(as_tuple_list=True))
            qt_target_mkspec_output = configure_cmake_project(
                qt_target_mkspec_dir,
                self._cmake_command,
                temp_prefix_build_path=config_tests_dir,
                cmake_cache_args=cmake_cache_args)

            qt_target_mkspec_info = parse_cmake_project_message_info(qt_target_mkspec_output)
            qt_target_mkspec_info = qt_target_mkspec_info['qt_info']

            return qt_target_mkspec_info
