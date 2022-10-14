# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

from pathlib import Path
import configparser
from configparser import ConfigParser
import shutil
import logging
import os


class Config:
    """
    Wrapper class around config file, whose options are used to control the executable creation
    """

    def __init__(self, config_file: Path) -> None:
        self.config_file = config_file
        self.parser = ConfigParser(comment_prefixes="/", allow_no_value=True)
        if not self.config_file.exists():
            logging.info(f"[DEPLOY]: Creating config file {self.config_file}")
            shutil.copy(Path(__file__).parent / "default.spec", self.config_file)
        else:
            print(f"Using existing config file {config_file}")
        self.parser.read(self.config_file)

        self.project_dir = None
        if self.get_value("app", "project_dir"):
            self.project_dir = Path(self.get_value("app", "project_dir")).absolute()

        self.qml_files = []
        config_qml_files = self.get_value("qt", "qml_files")
        if config_qml_files and self.project_dir:
            self.qml_files = [Path(self.project_dir) / file for file in config_qml_files.split(",")]

    def update_config(self):
        logging.info("[DEPLOY] Creating {config_file}")
        with open(self.config_file, "w+") as config_file:
            self.parser.write(config_file, space_around_delimiters=True)

    def set_value(self, section: str, key: str, new_value: str):
        try:
            current_value = self.get_value(section, key)
            if current_value != new_value:
                self.parser.set(section, key, new_value)
        except configparser.NoOptionError:
            logging.warning(f"[DEPLOY]: key {key} does not exist")
        except configparser.NoSectionError:
            logging.warning(f"[DEPLOY]: section {section} does not exist")

    def get_value(self, section: str, key: str):
        try:
            return self.parser.get(section, key)
        except configparser.NoOptionError:
            logging.warning(f"[DEPLOY]: key {key} does not exist")
        except configparser.NoSectionError:
            logging.warning(f"[DEPLOY]: section {section} does not exist")

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
            logging.exception(
                f"[DEPLOY]: No {config_property_key} specified in config file or as cli option"
            )
            raise

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

    def find_and_set_qml_files(self):
        """Fetches all the qml_files in the folder and sets them if the
        field qml_files is empty in the config_dir"""

        if self.project_dir:
            qml_files_str = self.get_value("qt", "qml_files")
            self.qml_files = []
            for file in qml_files_str.split(","):
                if file:
                    self.qml_files.append(Path(self.project_dir) / file)
        else:
            qml_files_temp = None
            source_file = (
                Path(self.get_value("app", "input_file"))
                if self.get_value("app", "input_file")
                else None
            )
            python_exe = (
                Path(self.get_value("python", "python_path"))
                if self.get_value("python", "python_path")
                else None
            )
            if source_file and python_exe:
                if not self.qml_files:
                    qml_files_temp = list(source_file.parent.glob("**/*.qml"))

                # add all QML files, excluding the ones shipped with installed PySide6
                # The QML files shipped with PySide6 gets added if venv is used,
                # because of recursive glob
                if python_exe.parent.parent == source_file.parent:
                    # python venv path is inside the main source dir
                    qml_files_temp = list(
                        set(qml_files_temp) - set(python_exe.parent.parent.rglob("*.qml"))
                    )

                if len(qml_files_temp) > 500:
                    if "site-packages" in str(qml_files_temp[-1]):
                        logging.warning(
                            "You seem to include a lot of QML files from a \
                                            local virtual env. Are they intended?"
                        )
                    else:
                        logging.warning(
                            "You seem to include a lot of QML files. \
                                        Are they intended?"
                        )

                if qml_files_temp:
                    extra_qml_files = [Path(file) for file in qml_files_temp]
                    self.qml_files.extend(extra_qml_files)
                    self.set_value(
                        "qt", "qml_files", ",".join([str(file) for file in self.qml_files])
                    )
                    logging.info("[DEPLOY] QML files identified and set in config_file")

    def find_and_set_project_dir(self):
        source_file = (
            Path(self.get_value("app", "input_file"))
            if self.get_value("app", "input_file")
            else None
        )

        if self.qml_files and source_file:
            paths = self.qml_files.copy()
            paths.append(source_file.absolute())
            self.project_dir = Path(os.path.commonpath(paths=paths))

            # update all qml paths
            logging.info("[DEPLOY] Update QML files paths to relative paths")
            qml_relative_paths = ",".join(
                [str(qml_file.relative_to(self.project_dir)) for qml_file in self.qml_files]
            )
            self.set_value("qt", "qml_files", qml_relative_paths)
        else:
            self.project_dir = source_file.parent

        # update input_file path
        logging.info("[DEPLOY] Update input_file path")
        self.set_value("app", "input_file", str(source_file.relative_to(self.project_dir)))

        logging.info("[DEPLOY] Update project_dir path")
        if self.project_dir != Path.cwd():
            self.set_value("app", "project_dir", str(self.project_dir))
        else:
            self.set_value("app", "project_dir", str(self.project_dir.relative_to(Path.cwd())))
