# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

import sys
import configparser
import logging
import tempfile
import warnings
from configparser import ConfigParser
from pathlib import Path
from enum import Enum

from project import ProjectData
from . import (DEFAULT_APP_ICON, DEFAULT_IGNORE_DIRS, DesignStudio, find_pyside_modules,
               find_permission_categories, QtDependencyReader, run_qmlimportscanner)

# Some QML plugins like QtCore are excluded from this list as they don't contribute much to
# executable size. Excluding them saves the extra processing of checking for them in files
EXCLUDED_QML_PLUGINS = {"QtQuick", "QtQuick3D", "QtCharts", "QtWebEngine", "QtTest", "QtSensors"}

PERMISSION_MAP = {"Bluetooth": "NSBluetoothAlwaysUsageDescription:BluetoothAccess",
                  "Camera": "NSCameraUsageDescription:CameraAccess",
                  "Microphone": "NSMicrophoneUsageDescription:MicrophoneAccess",
                  "Contacts": "NSContactsUsageDescription:ContactsAccess",
                  "Calendar": "NSCalendarsUsageDescription:CalendarAccess",
                  # for iOS NSLocationWhenInUseUsageDescription and
                  # NSLocationAlwaysAndWhenInUseUsageDescription are also required.
                  "Location": "NSLocationUsageDescription:LocationAccess",
                  }


class BaseConfig:
    """Wrapper class around any .spec file with function to read and set values for the .spec file
    """
    def __init__(self, config_file: Path, comment_prefixes: str = "/",
                 existing_config_file: bool = False) -> None:
        self.config_file = config_file
        self.existing_config_file = existing_config_file
        self.parser = ConfigParser(comment_prefixes=comment_prefixes, strict=False,
                                   allow_no_value=True)
        self.parser.read(self.config_file)

    def update_config(self):
        logging.info(f"[DEPLOY] Creating {self.config_file}")

        # This section of code is done to preserve the formatting of the original deploy.spec
        # file where there is blank line before the comments
        with tempfile.NamedTemporaryFile('w+', delete=False) as temp_file:
            self.parser.write(temp_file, space_around_delimiters=True)
            temp_file_path = temp_file.name

        # Read the temporary file and write back to the original file with blank lines before
        # comments
        with open(temp_file_path, 'r') as temp_file, open(self.config_file, 'w') as config_file:
            previous_line = None
            for line in temp_file:
                if (line.lstrip().startswith('#') and previous_line is not None
                   and not previous_line.lstrip().startswith('#')):
                    config_file.write('\n')
                config_file.write(line)
                previous_line = line

        # Clean up the temporary file
        Path(temp_file_path).unlink()

    def set_value(self, section: str, key: str, new_value: str, raise_warning: bool = True):
        try:
            current_value = self.get_value(section, key, ignore_fail=True)
            if current_value != new_value:
                self.parser.set(section, key, new_value)
        except configparser.NoOptionError:
            if raise_warning:
                logging.warning(f"[DEPLOY] Key {key} does not exist")
        except configparser.NoSectionError:
            if raise_warning:
                logging.warning(f"[DEPLOY] Section {section} does not exist")

    def get_value(self, section: str, key: str, ignore_fail: bool = False):
        try:
            return self.parser.get(section, key)
        except configparser.NoOptionError:
            if not ignore_fail:
                logging.warning(f"[DEPLOY] Key {key} does not exist")
        except configparser.NoSectionError:
            if not ignore_fail:
                logging.warning(f"[DEPLOY] Section {section} does not exist")


class Config(BaseConfig):
    """
    Wrapper class around pysidedeploy.spec file, whose options are used to control the executable
    creation
    """

    def __init__(self, config_file: Path, source_file: Path, python_exe: Path, dry_run: bool,
                 existing_config_file: bool = False, extra_ignore_dirs: list[str] = None,
                 name: str = None):
        super().__init__(config_file=config_file, existing_config_file=existing_config_file)

        self.extra_ignore_dirs = extra_ignore_dirs
        self._dry_run = dry_run
        self.qml_modules = set()
        # set source_file
        self.source_file = Path(
            self.set_or_fetch(config_property_val=source_file, config_property_key="input_file")
        ).resolve()

        # set python path
        self.python_path = Path(
            self.set_or_fetch(
                config_property_val=python_exe,
                config_property_key="python_path",
                config_property_group="python",
            )
        )

        # set application name
        self.title = self.set_or_fetch(config_property_val=name, config_property_key="title")

        # set application icon
        config_icon = self.get_value("app", "icon")
        if config_icon:
            self._icon = str(Path(config_icon).resolve())
        else:
            self.icon = DEFAULT_APP_ICON

        proj_dir = self.get_value("app", "project_dir")
        if proj_dir:
            self._project_dir = Path(proj_dir).resolve()
        else:
            self.project_dir = self._find_project_dir()

        exe_directory = self.get_value("app", "exec_directory")
        if exe_directory:
            self._exe_dir = Path(exe_directory).absolute()
        else:
            self.exe_dir = self._find_exe_dir()

        self._project_file = None
        proj_file = self.get_value("app", "project_file")
        if proj_file:
            self._project_file = self.project_dir / proj_file
        else:
            proj_file = self._find_project_file()
            if proj_file:
                self.project_file = proj_file

        self.project_data = None
        if self.project_file and self.project_file.exists():
            self.project_data = ProjectData(project_file=self.project_file)

        self._qml_files = []
        config_qml_files = self.get_value("qt", "qml_files")
        if config_qml_files and self.project_dir and self.existing_config_file:
            self._qml_files = [Path(self.project_dir)
                               / file for file in config_qml_files.split(",")]
        else:
            self.qml_files = self._find_qml_files()

        self._excluded_qml_plugins = []
        excl_qml_plugins = self.get_value("qt", "excluded_qml_plugins")
        if excl_qml_plugins and self.existing_config_file:
            self._excluded_qml_plugins = excl_qml_plugins.split(",")
        else:
            self.excluded_qml_plugins = self._find_excluded_qml_plugins()

        if DesignStudio.isDSProject(self.source_file):
            self._generated_files_path = self.project_dir / "Python" / "deployment"
        else:
            self._generated_files_path = self.project_dir / "deployment"

        self.modules = []

    def set_or_fetch(self, config_property_val, config_property_key, config_property_group="app"):
        """
        Set the configuration value if provided, otherwise fetch the existing value.
        Raise an exception if neither is available.

        :param value: The value to set if provided.
        :param key: The configuration key.
        :param group: The configuration group (default is "app").
        :return: The configuration value.
        :raises RuntimeError: If no value is provided and no existing value is found.
        """
        existing_value = self.get_value(config_property_group, config_property_key)

        if config_property_val:
            self.set_value(config_property_group, config_property_key, str(config_property_val))
            return config_property_val
        elif existing_value:
            return existing_value
        else:
            raise RuntimeError(
                f"[DEPLOY] No value for {config_property_key} specified in config file or as cli"
                " option"
            )

    @property
    def dry_run(self):
        return self._dry_run

    @property
    def generated_files_path(self):
        return self._generated_files_path

    @property
    def qml_files(self):
        return self._qml_files

    @qml_files.setter
    def qml_files(self, qml_files):
        self._qml_files = qml_files
        qml_files = [str(file.absolute().relative_to(self.project_dir.absolute()))
                     if file.absolute().is_relative_to(self.project_dir) else str(file.absolute())
                     for file in self.qml_files]
        self.set_value("qt", "qml_files", ",".join(qml_files))

    @property
    def project_dir(self):
        return self._project_dir

    @project_dir.setter
    def project_dir(self, project_dir):
        self._project_dir = project_dir
        self.set_value("app", "project_dir", str(project_dir))

    @property
    def project_file(self):
        return self._project_file

    @project_file.setter
    def project_file(self, project_file):
        self._project_file = project_file
        self.set_value("app", "project_file", str(project_file.relative_to(self.project_dir)))

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = title

    @property
    def icon(self):
        return self._icon

    @icon.setter
    def icon(self, icon):
        self._icon = icon
        self.set_value("app", "icon", icon)

    @property
    def source_file(self):
        return self._source_file

    @source_file.setter
    def source_file(self, source_file: Path):
        self._source_file = source_file
        # FIXME: Remove when new DS is released
        # for DS project, set self._source_file to main_patch.py, but don't change the value
        # in the config file as main_patch.py is a temporary file
        if DesignStudio.isDSProject(source_file):
            self._source_file = DesignStudio(source_file).ds_source_file
        self.set_value("app", "input_file", str(source_file))

    @property
    def python_path(self):
        return self._python_path

    @python_path.setter
    def python_path(self, python_path: Path):
        self._python_path = python_path

    @property
    def extra_args(self):
        return self.get_value("nuitka", "extra_args")

    @extra_args.setter
    def extra_args(self, extra_args):
        self.set_value("nuitka", "extra_args", extra_args)

    @property
    def excluded_qml_plugins(self):
        return self._excluded_qml_plugins

    @excluded_qml_plugins.setter
    def excluded_qml_plugins(self, excluded_qml_plugins):
        self._excluded_qml_plugins = excluded_qml_plugins
        if excluded_qml_plugins:  # check required for Android
            self.set_value("qt", "excluded_qml_plugins", ",".join(excluded_qml_plugins))

    @property
    def exe_dir(self):
        return self._exe_dir

    @exe_dir.setter
    def exe_dir(self, exe_dir: Path):
        self._exe_dir = exe_dir
        self.set_value("app", "exec_directory", str(exe_dir))

    @property
    def modules(self):
        return self._modules

    @modules.setter
    def modules(self, modules):
        self._modules = modules
        self.set_value("qt", "modules", ",".join(modules))

    def _find_qml_files(self):
        """
        Fetches all the qml_files in the folder and sets them if the
        field qml_files is empty in the config_file
        """

        qml_files = []
        if self.project_data:
            qml_files = [(self.project_dir / str(qml_file)) for qml_file in
                         self.project_data.qml_files]
            for sub_project_file in self.project_data.sub_projects_files:
                qml_files.extend([self.project_dir / str(qml_file) for qml_file in
                                  ProjectData(project_file=sub_project_file).qml_files])
        else:
            # Filter out files from DEFAULT_IGNORE_DIRS
            qml_files = [
                file for file in self.project_dir.glob("**/*.qml")
                if all(part not in file.parts for part in DEFAULT_IGNORE_DIRS)
            ]

            if len(qml_files) > 500:
                warnings.warn(
                    "You seem to include a lot of QML files from "
                    f"{self.project_dir}. This can lead to errors in deployment."
                )

        return qml_files

    def _find_project_dir(self) -> Path:
        if DesignStudio.isDSProject(self.source_file):
            ds = DesignStudio(self.source_file)
            project_dir = ds.project_dir
        else:
            # there is no other way to find the project_dir than assume it is the parent directory
            # of source_file
            project_dir = self.source_file.parent
        return project_dir

    def _find_project_file(self) -> Path:
        if self.project_dir:
            files = list(self.project_dir.glob("*.pyproject"))
        else:
            raise RuntimeError("[DEPLOY] Project directory not set in config file")

        if not files:
            logging.info("[DEPLOY] No .pyproject file found. Project file not set")
        elif len(files) > 1:
            warnings.warn("DEPLOY: More that one .pyproject files found. Project file not set")
        else:
            return files[0]

        return None

    def _find_excluded_qml_plugins(self) -> set:
        excluded_qml_plugins = None
        if self.qml_files:
            self.qml_modules = set(run_qmlimportscanner(project_dir=self.project_dir,
                                                        dry_run=self.dry_run))
            excluded_qml_plugins = EXCLUDED_QML_PLUGINS.difference(self.qml_modules)

            # needed for dry_run testing
            excluded_qml_plugins = sorted(excluded_qml_plugins)

        return excluded_qml_plugins

    def _find_exe_dir(self) -> Path:
        exe_dir = None
        if self.project_dir == Path.cwd():
            exe_dir = self.project_dir.relative_to(Path.cwd())
        else:
            exe_dir = self.project_dir
        return exe_dir

    def _find_pysidemodules(self):
        modules = find_pyside_modules(project_dir=self.project_dir,
                                      extra_ignore_dirs=self.extra_ignore_dirs,
                                      project_data=self.project_data)
        logging.info("The following PySide modules were found from the Python files of "
                     f"the project {modules}")
        return modules

    def _find_qtquick_modules(self):
        """Identify if QtQuick is used in QML files and add them as dependency
        """
        extra_modules = []
        if not self.qml_modules and self.qml_files:
            self.qml_modules = set(run_qmlimportscanner(project_dir=self.project_dir,
                                                        dry_run=self.dry_run))

        if "QtQuick" in self.qml_modules:
            extra_modules.append("Quick")

        if "QtQuick.Controls" in self.qml_modules:
            extra_modules.append("QuickControls2")

        return extra_modules


class DesktopConfig(Config):
    """Wrapper class around pysidedeploy.spec, but specific to Desktop deployment
    """
    class NuitkaMode(Enum):
        ONEFILE = "onefile"
        STANDALONE = "standalone"

    def __init__(self, config_file: Path, source_file: Path, python_exe: Path, dry_run: bool,
                 existing_config_file: bool = False, extra_ignore_dirs: list[str] = None,
                 mode: str = "onefile", name: str = None):
        super().__init__(config_file, source_file, python_exe, dry_run, existing_config_file,
                         extra_ignore_dirs, name=name)
        self.dependency_reader = QtDependencyReader(dry_run=self.dry_run)
        modls = self.get_value("qt", "modules")
        if modls:
            self._modules = modls.split(",")
        else:
            modls = self._find_pysidemodules()
            modls += self._find_qtquick_modules()
            modls += self._find_dependent_qt_modules(modules=modls)
            # remove duplicates
            self.modules = list(set(modls))

        self._qt_plugins = []
        if self.get_value("qt", "plugins"):
            self._qt_plugins = self.get_value("qt", "plugins").split(",")
        else:
            self.qt_plugins = self.dependency_reader.find_plugin_dependencies(self.modules,
                                                                              python_exe)

        self._permissions = []
        if sys.platform == "darwin":
            nuitka_macos_permissions = self.get_value("nuitka", "macos.permissions")
            if nuitka_macos_permissions:
                self._permissions = nuitka_macos_permissions.split(",")
            else:
                self.permissions = self._find_permissions()

        self._mode = self.NuitkaMode.ONEFILE
        if self.get_value("nuitka", "mode") == self.NuitkaMode.STANDALONE.value:
            self._mode = self.NuitkaMode.STANDALONE
        elif mode == self.NuitkaMode.STANDALONE.value:
            self.mode = self.NuitkaMode.STANDALONE

    @property
    def qt_plugins(self):
        return self._qt_plugins

    @qt_plugins.setter
    def qt_plugins(self, qt_plugins):
        self._qt_plugins = qt_plugins
        self.set_value("qt", "plugins", ",".join(qt_plugins))

    @property
    def permissions(self):
        return self._permissions

    @permissions.setter
    def permissions(self, permissions):
        self._permissions = permissions
        self.set_value("nuitka", "macos.permissions", ",".join(permissions))

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, mode: NuitkaMode):
        self._mode = mode
        self.set_value("nuitka", "mode", mode.value)

    def _find_dependent_qt_modules(self, modules: list[str]) -> list[str]:
        """
        Given pysidedeploy_config.modules, find all the other dependent Qt modules.
        """
        all_modules = set(modules)

        if not self.dependency_reader.lib_reader:
            warnings.warn(f"[DEPLOY] Unable to find {self.dependency_reader.lib_reader_name}. This "
                          "tool helps to find the Qt module dependencies of the application. "
                          "Skipping checking for dependencies.", category=RuntimeWarning)
            return []

        for module_name in modules:
            self.dependency_reader.find_dependencies(module=module_name, used_modules=all_modules)

        return list(all_modules)

    def _find_permissions(self):
        """
        Finds and sets the usage description string required for each permission requested by the
        macOS application.
        """
        permissions = []
        perm_categories = find_permission_categories(project_dir=self.project_dir,
                                                     extra_ignore_dirs=self.extra_ignore_dirs,
                                                     project_data=self.project_data)

        perm_categories_str = ",".join(perm_categories)
        logging.info(f"[DEPLOY] Usage descriptions for the {perm_categories_str} will be added to "
                     "the Info.plist file of the macOS application bundle")

        # handling permissions
        for perm_category in perm_categories:
            if perm_category in PERMISSION_MAP:
                permissions.append(PERMISSION_MAP[perm_category])

        return permissions
