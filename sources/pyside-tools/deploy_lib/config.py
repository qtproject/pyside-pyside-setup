# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import sys
import configparser
import logging
import warnings
from configparser import ConfigParser
from typing import List
from pathlib import Path

from project import ProjectData
from . import (DEFAULT_APP_ICON, find_pyside_modules, find_permission_categories,
               QtDependencyReader, run_qmlimportscanner)

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
        with open(self.config_file, "w+") as config_file:
            self.parser.write(config_file, space_around_delimiters=True)

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
                 existing_config_file: bool = False, extra_ignore_dirs: List[str] = None):
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

        self.title = self.get_value("app", "title")

        # set application icon
        config_icon = self.get_value("app", "icon")
        if config_icon:
            self.icon = str(Path(config_icon).resolve())
        else:
            self.icon = DEFAULT_APP_ICON

        self.project_dir = None
        if self.get_value("app", "project_dir"):
            self.project_dir = Path(self.get_value("app", "project_dir")).absolute()
        else:
            self._find_and_set_project_dir()

        self.exe_dir = None
        if self.get_value("app", "exec_directory"):
            self.exe_dir = Path(self.get_value("app", "exec_directory")).absolute()
        else:
            self._find_and_set_exe_dir()

        self.project_data: ProjectData = None
        if self.get_value("app", "project_file"):
            project_file = Path(self.get_value("app", "project_file")).absolute()
            self.project_data = ProjectData(project_file=project_file)
        else:
            self._find_and_set_project_file()

        self.qml_files = []
        config_qml_files = self.get_value("qt", "qml_files")
        if config_qml_files and self.project_dir and self.existing_config_file:
            self.qml_files = [Path(self.project_dir) / file for file in config_qml_files.split(",")]
        else:
            self._find_and_set_qml_files()

        self.excluded_qml_plugins = []
        if self.get_value("qt", "excluded_qml_plugins") and self.existing_config_file:
            self.excluded_qml_plugins = self.get_value("qt", "excluded_qml_plugins").split(",")
        else:
            self._find_and_set_excluded_qml_plugins()

        self._generated_files_path = self.project_dir / "deployment"

        self.modules = []

    def set_or_fetch(self, config_property_val, config_property_key, config_property_group="app"):
        """
        Write to config_file if 'config_property_key' is known without config_file
        Fetch and return from config_file if 'config_property_key' is unknown, but
        config_file exists
        Otherwise, raise an exception
        """
        if config_property_val:
            self.set_value(config_property_group, config_property_key, str(config_property_val))
            return config_property_val
        elif self.get_value(config_property_group, config_property_key):
            return self.get_value(config_property_group, config_property_key)
        else:
            raise RuntimeError(
                f"[DEPLOY] No {config_property_key} specified in config file or as cli option"
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

    @property
    def project_dir(self):
        return self._project_dir

    @project_dir.setter
    def project_dir(self, project_dir):
        self._project_dir = project_dir

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = title
        self.set_value("app", "title", title)

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

    @property
    def exe_dir(self):
        return self._exe_dir

    @exe_dir.setter
    def exe_dir(self, exe_dir: Path):
        self._exe_dir = exe_dir

    @property
    def modules(self):
        return self._modules

    @modules.setter
    def modules(self, modules):
        self._modules = modules
        self.set_value("qt", "modules", ",".join(modules))

    def _find_and_set_qml_files(self):
        """Fetches all the qml_files in the folder and sets them if the
        field qml_files is empty in the config_dir"""

        if self.project_data:
            qml_files = self.project_data.qml_files
            for sub_project_file in self.project_data.sub_projects_files:
                qml_files.extend(ProjectData(project_file=sub_project_file).qml_files)
            self.qml_files = qml_files
        else:
            qml_files_temp = None
            if self.source_file and self.python_path:
                if not self.qml_files:
                    qml_files_temp = list(self.source_file.parent.glob("**/*.qml"))

                # add all QML files, excluding the ones shipped with installed PySide6
                # The QML files shipped with PySide6 gets added if venv is used,
                # because of recursive glob
                if self.python_path.parent.parent == self.source_file.parent:
                    # python venv path is inside the main source dir
                    qml_files_temp = list(
                        set(qml_files_temp) - set(self.python_path.parent.parent.rglob("*.qml"))
                    )

                if len(qml_files_temp) > 500:
                    if "site-packages" in str(qml_files_temp[-1]):
                        raise RuntimeError(
                            "You are including a lot of QML files from a local virtual env."
                            " This can lead to errors in deployment."
                        )
                    else:
                        warnings.warn(
                            "You seem to include a lot of QML files. This can lead to errors in "
                            "deployment."
                        )

                if qml_files_temp:
                    extra_qml_files = [Path(file) for file in qml_files_temp]
                    self.qml_files.extend(extra_qml_files)
        if self.qml_files:
            self.set_value(
                "qt",
                "qml_files",
                ",".join([str(file.absolute().relative_to(self.project_dir))
                          for file in self.qml_files]),
            )
            logging.info("[DEPLOY] QML files identified and set in config_file")

    def _find_and_set_project_dir(self):
        # there is no other way to find the project_dir than assume it is the parent directory
        # of source_file
        self.project_dir = self.source_file.parent

        # update input_file path
        self.set_value("app", "input_file", str(self.source_file.relative_to(self.project_dir)))

        if self.project_dir != Path.cwd():
            self.set_value("app", "project_dir", str(self.project_dir))
        else:
            self.set_value("app", "project_dir", str(self.project_dir.relative_to(Path.cwd())))

    def _find_and_set_project_file(self):
        if self.project_dir:
            files = list(self.project_dir.glob("*.pyproject"))
        else:
            logging.exception("[DEPLOY] Project directory not set in config file")
            raise

        if not files:
            logging.info("[DEPLOY] No .pyproject file found. Project file not set")
        elif len(files) > 1:
            logging.warning("DEPLOY: More that one .pyproject files found. Project file not set")
            raise
        else:
            self.project_data = ProjectData(files[0])
            self.set_value("app", "project_file", str(files[0].relative_to(self.project_dir)))
            logging.info(f"[DEPLOY] Project file {files[0]} found and set in config file")

    def _find_and_set_excluded_qml_plugins(self):
        if self.qml_files:
            self.qml_modules = set(run_qmlimportscanner(qml_files=self.qml_files,
                                                        dry_run=self.dry_run))
            self.excluded_qml_plugins = EXCLUDED_QML_PLUGINS.difference(self.qml_modules)

            # needed for dry_run testing
            self.excluded_qml_plugins = sorted(self.excluded_qml_plugins)

            if self.excluded_qml_plugins:
                self.set_value("qt", "excluded_qml_plugins", ",".join(self.excluded_qml_plugins))

    def _find_and_set_exe_dir(self):
        if self.project_dir == Path.cwd():
            self.exe_dir = self.project_dir.relative_to(Path.cwd())
        else:
            self.exe_dir = self.project_dir
        self.exe_dir = Path(
            self.set_or_fetch(
                config_property_val=self.exe_dir, config_property_key="exec_directory"
            )
        ).absolute()

    def _find_and_set_pysidemodules(self):
        self.modules = find_pyside_modules(project_dir=self.project_dir,
                                           extra_ignore_dirs=self.extra_ignore_dirs,
                                           project_data=self.project_data)
        logging.info("The following PySide modules were found from the Python files of "
                     f"the project {self.modules}")

    def _find_and_set_qtquick_modules(self):
        """Identify if QtQuick is used in QML files and add them as dependency
        """
        extra_modules = []
        if not self.qml_modules:
            self.qml_modules = set(run_qmlimportscanner(qml_files=self.qml_files,
                                                        dry_run=self.dry_run))

        if "QtQuick" in self.qml_modules:
            extra_modules.append("Quick")

        if "QtQuick.Controls" in self.qml_modules:
            extra_modules.append("QuickControls2")

        self.modules += extra_modules


class DesktopConfig(Config):
    """Wrapper class around pysidedeploy.spec, but specific to Desktop deployment
    """
    def __init__(self, config_file: Path, source_file: Path, python_exe: Path, dry_run: bool,
                 existing_config_file: bool = False, extra_ignore_dirs: List[str] = None):
        super().__init__(config_file, source_file, python_exe, dry_run, existing_config_file,
                         extra_ignore_dirs)
        self.dependency_reader = QtDependencyReader(dry_run=self.dry_run)
        if self.get_value("qt", "modules"):
            self.modules = self.get_value("qt", "modules").split(",")
        else:
            self._find_and_set_pysidemodules()
            self._find_and_set_qtquick_modules()
            self._find_dependent_qt_modules()

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
                self._find_and_set_permissions()

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

    def _find_dependent_qt_modules(self):
        """
        Given pysidedeploy_config.modules, find all the other dependent Qt modules.
        """
        all_modules = set(self.modules)

        if not self.dependency_reader.lib_reader:
            warnings.warn(f"[DEPLOY] Unable to find {self.dependency_reader.lib_reader_name}. This "
                          "tool helps to find the Qt module dependencies of the application. "
                          "Skipping checking for dependencies.", category=RuntimeWarning)
            return

        for module_name in self.modules:
            self.dependency_reader.find_dependencies(module=module_name, used_modules=all_modules)

        self.modules = list(all_modules)

    def _find_and_set_permissions(self):
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

        self.permissions = permissions
