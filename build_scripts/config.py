# Copyright (C) 2018 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from . import PYPROJECT_PATH, PYSIDE, PYSIDE_MODULE, SHIBOKEN
from .log import LogLevel, log
from .utils import available_pyside_tools, Singleton

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


class Config(metaclass=Singleton):
    def __init__(self):
        # Constants
        self._build_type_all = "all"
        self._invocation_type_top_level = "top-level"
        self._invocation_type_internal = "internal"

        # The keyword arguments which will be given to setuptools.setup
        self.setup_kwargs = {}

        # The setup.py invocation type.
        # top-level
        # internal
        self.invocation_type: str = ""

        # The type of the top-level build.
        # all - build shiboken6 module, shiboken6-generator and PySide6
        #       modules
        # shiboken6 - build only shiboken6 module
        # shiboken6-generator - build only the shiboken6-generator
        # pyside6 - build only PySide6 modules
        self.build_type: str = ""

        # The internal build type, used for internal invocations of
        # setup.py to build a specific module only.
        self.internal_build_type: str = ""

        # Options that can be given to --build-type and
        # --internal-build-type
        self.shiboken_module_option_name = SHIBOKEN
        self.shiboken_generator_option_name = f"{SHIBOKEN}-generator"
        self.pyside_option_name = PYSIDE

        # Names to be passed to setuptools.setup() name key,
        # so not package name, but rather project name as it appears
        # in the wheel name and on PyPi.
        self.shiboken_module_st_name: str = SHIBOKEN
        self.shiboken_generator_st_name: str = f"{SHIBOKEN}-generator"
        self.pyside_st_name: str = PYSIDE_MODULE

        # Path to CMake toolchain file when intending to cross compile
        # the project.
        self.cmake_toolchain_file: str | os.PathLike = ""

        # Store where host shiboken is built during a cross-build.
        self.shiboken_host_query_path: str = ""

        self.setup_script_dir: str | os.PathLike = ""

        # Getting data from base pyproject.toml file to be consistent

        if not PYPROJECT_PATH.exists():
            log.error("'pyproject.toml.base' not found in '{pyproject_path}'")

        with open(PYPROJECT_PATH, "rb") as f:
            _pyproject_data = tomllib.load(f)["project"]

        self.setup_kwargs: dict[str, Any] = {}
        self.setup_kwargs['long_description_content_type'] = 'text/markdown'

        self.setup_kwargs['keywords'] = _pyproject_data["keywords"]
        _author = _pyproject_data["authors"][0]
        self.setup_kwargs['author'] = _author["name"]
        self.setup_kwargs['author_email'] = _author["email"]
        self.setup_kwargs['url'] = _pyproject_data["urls"]["Homepage"]
        self.setup_kwargs['license'] = _pyproject_data["license"]["text"]
        self.setup_kwargs['python_requires'] = _pyproject_data["requires-python"]

        self.classifiers = _pyproject_data["classifiers"]
        self.setup_kwargs['classifiers'] = self.classifiers

    def init_config(self,
                    build_type="",
                    internal_build_type="",
                    cmd_class_dict=None,
                    package_version=None,
                    ext_modules=None,
                    setup_script_dir: str | os.PathLike = "",
                    cmake_toolchain_file: str | os.PathLike = "",
                    log_level=LogLevel.INFO,
                    qt_install_dir: str | os.PathLike = ""):
        """
        Sets up the global singleton config which is used in many parts
        of the setup process.
        """

        # if --internal-build-type was passed, it means that this is a
        # sub-invocation to build a specific package.
        if internal_build_type:
            self.set_is_internal_invocation()
            self.set_internal_build_type(internal_build_type)
        else:
            self.set_is_top_level_invocation()

        # --build-type was specified explicitly, so set it. Otherwise
        # default to all.
        if build_type:
            self.build_type = build_type
        else:
            self.build_type = self._build_type_all

        self.setup_script_dir = Path(setup_script_dir)

        self.cmake_toolchain_file = cmake_toolchain_file

        self.setup_kwargs['long_description'] = self.get_long_description()
        self.setup_kwargs['cmdclass'] = cmd_class_dict
        self.setup_kwargs['version'] = package_version

        if log_level == LogLevel.QUIET:
            # Tells setuptools to be quiet, and only print warnings or errors.
            # Makes way less noise in the terminal when building.
            self.setup_kwargs['verbose'] = 0

        # Setting these two keys is still a bit of a discussion point.
        # In general not setting them will allow using "build" and
        # "bdist_wheel" just fine. What they do, is they specify to the
        # setuptools.command.build_py command that certain pure python
        # modules (.py files) exist in the specified package location,
        # and that they should be copied over to the setuptools build
        # dir.
        # But it doesn't really make sense for us, because we copy all
        # the necessary files to the build dir via prepare_packages()
        # function anyway.
        # If we don't set them, the build_py sub-command will be
        # skipped, but the build command will still be executed, which
        # is where we run cmake / make.
        # The only plausible usage of it, is if we will implement a
        # correctly functioning setup.py develop command (or bdist_egg).
        # But currently that doesn't seem to work.
        self.setup_kwargs['packages'] = self.get_setup_tools_packages_for_current_build()
        self.setup_kwargs['package_dir'] = self.get_package_name_to_dir_path_mapping()

        # Add a bogus extension module (will never be built here since
        # we are overriding the build command to do it using cmake) so
        # things like bdist_egg will know that there are extension
        # modules and will name the dist with the full platform info.
        self.setup_kwargs['ext_modules'] = ext_modules

        package_name = self.package_name()

        if self.internal_build_type == self.shiboken_module_option_name:
            self.setup_kwargs['name'] = self.shiboken_module_st_name
            self.setup_kwargs['description'] = "Python / C++ bindings helper module"
            self.setup_kwargs['entry_points'] = {}

        elif self.internal_build_type == self.shiboken_generator_option_name:
            self.setup_kwargs['name'] = self.shiboken_generator_st_name
            self.setup_kwargs['description'] = "Python / C++ bindings generator"
            self.setup_kwargs['install_requires'] = [
                f"{self.shiboken_module_st_name}=={package_version}"
            ]
            self.setup_kwargs['entry_points'] = {
                'console_scripts': [
                    f'{SHIBOKEN} = {package_name}.scripts.shiboken_tool:main',
                    f'{SHIBOKEN}-genpyi = {package_name}.scripts.shiboken_tool:genpyi',
                ]
            }

        elif self.internal_build_type == self.pyside_option_name:
            self.setup_kwargs['name'] = self.pyside_st_name
            self.setup_kwargs['description'] = (
                "Python bindings for the Qt cross-platform application and UI framework"
            )
            self.setup_kwargs['install_requires'] = [
                f"{self.shiboken_module_st_name}=={package_version}"
            ]
            if qt_install_dir:
                _pyside_tools = available_pyside_tools(qt_tools_path=Path(qt_install_dir))

                # replacing pyside6-android_deploy by pyside6-android-deploy for consistency
                # Also, the tool should not exist in any other platform than Linux and macOS
                _console_scripts = []
                if ("android_deploy" in _pyside_tools) and sys.platform in ["linux", "darwin"]:
                    _console_scripts = [(f"{PYSIDE}-android-deploy ="
                                        " PySide6.scripts.pyside_tool:android_deploy")]
                _pyside_tools.remove("android_deploy")

                _console_scripts.extend([f'{PYSIDE}-{tool} = {package_name}.scripts.pyside_tool:'
                                         f'{tool}' for tool in _pyside_tools])

                self.setup_kwargs['entry_points'] = {'console_scripts': _console_scripts}

    def get_long_description(self):
        readme_filename = 'README.md'
        changes_filename = 'CHANGES.rst'

        if self.is_internal_shiboken_module_build():
            readme_filename = f'README.{SHIBOKEN}.md'
        elif self.is_internal_shiboken_generator_build():
            readme_filename = f'README.{SHIBOKEN}-generator.md'
        elif self.is_internal_pyside_build():
            readme_filename = f'README.{PYSIDE}.md'

        with open(Path(self.setup_script_dir) / readme_filename) as f:
            readme = f.read()

        # Don't include CHANGES.rst for now, because we have not decided
        # how to handle change files yet.
        include_changes = False
        if include_changes:
            try:
                changes = ''
                with open(Path(self.setup_script_dir) / changes_filename) as f:
                    changes = f.read()
            except Exception as e:
                log.error(f"Couldn't read contents of {changes_filename}. {e}")
                raise
            return f"{readme}\n\n{changes}"

        return readme

    def package_name(self):
        """
        Returns package name as it appears in Python's site-packages
        directory.

        Package names can only be delimited by underscores, and not by
        dashes.
        """
        if self.is_internal_shiboken_module_build():
            return SHIBOKEN
        elif self.is_internal_shiboken_generator_build():
            return f"{SHIBOKEN}_generator"
        elif self.is_internal_pyside_build():
            return PYSIDE_MODULE
        else:
            return None

    def get_setup_tools_packages_for_current_build(self):
        """
        Returns a list of packages for setup tools to consider in the
        build_py command, so that it can copy the pure python files.
        Not really necessary because it's done in prepare_packages()
        anyway.

        This is really just to satisfy some checks in setuptools
        build_py command, and if we ever properly implement the develop
        command.
        """
        if self.internal_build_type == self.pyside_option_name:
            return [
                config.package_name(),
            ]
        elif self.internal_build_type == self.shiboken_module_option_name:
            return [self.package_name()]
        else:
            return []

    def get_package_name_to_dir_path_mapping(self):
        """
        Used in setuptools.setup 'package_dir' argument to specify where
        the actual module packages are located.

        For example when building the shiboken module, setuptools will
        expect to find the "shiboken6" module sources under
        "sources/{SHIBOKEN}/shibokenmodule".

        This is really just to satisfy some checks in setuptools
        build_py command, and if we ever properly implement the develop
        command.
        """
        if self.is_internal_shiboken_module_build():
            return {
                self.package_name(): f"sources/{SHIBOKEN}/shibokenmodule"
            }
        elif self.is_internal_shiboken_generator_build():
            # This is left empty on purpose, because the shiboken
            # generator doesn't have a python module for now.
            return {}
        elif self.is_internal_pyside_build():
            return {
                self.package_name(): f"sources/{PYSIDE}/{PYSIDE_MODULE}",
            }
        else:
            return {}

    def get_buildable_extensions(self):
        """
        Used by PysideBuild.run to build the CMake projects.
        :return: A list of directory names under the sources directory.
        """
        if self.is_internal_shiboken_module_build() or self.is_internal_shiboken_generator_build():
            return [SHIBOKEN]
        elif self.is_internal_pyside_build():
            return [PYSIDE, 'pyside-tools']
        return None

    def set_is_top_level_invocation(self):
        self.invocation_type = self._invocation_type_top_level

    def set_is_internal_invocation(self):
        self.invocation_type = self._invocation_type_internal

    def is_top_level_invocation(self):
        return self.invocation_type == self._invocation_type_top_level

    def is_internal_invocation(self):
        return self.invocation_type == self._invocation_type_internal

    def is_top_level_build_all(self):
        return self.build_type == self._build_type_all

    def is_top_level_build_shiboken_module(self):
        return self.build_type == self.shiboken_module_option_name

    def is_top_level_build_shiboken_generator(self):
        return self.build_type == self.shiboken_generator_option_name

    def is_top_level_build_pyside(self):
        return self.build_type == self.pyside_option_name

    def is_cross_compile(self):
        if not self.cmake_toolchain_file:
            return False
        return True

    def set_internal_build_type(self, internal_build_type):
        self.internal_build_type = internal_build_type

    def is_internal_shiboken_module_build(self):
        return self.internal_build_type == self.shiboken_module_option_name

    def is_internal_shiboken_generator_build(self):
        return self.internal_build_type == self.shiboken_generator_option_name

    def is_internal_pyside_build(self):
        return self.internal_build_type == self.pyside_option_name

    def is_internal_shiboken_generator_build_and_part_of_top_level_all(self):
        """
        Used to skip certain build rules and output, when we know that
        the CMake build of shiboken was already done as part of the
        top-level "all" build when shiboken6-module was built.
        """
        return self.is_internal_shiboken_generator_build() and self.is_top_level_build_all()

    def get_allowed_top_level_build_values(self):
        return [
            self._build_type_all,
            self.shiboken_module_option_name,
            self.shiboken_generator_option_name,
            self.pyside_option_name
        ]

    def get_allowed_internal_build_values(self):
        return [
            self.shiboken_module_option_name,
            self.shiboken_generator_option_name,
            self.pyside_option_name
        ]


config = Config()
