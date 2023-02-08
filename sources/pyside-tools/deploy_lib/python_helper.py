# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import sys
import os
import logging
from importlib import util
if sys.version_info >= (3, 8):
    from importlib.metadata import version
else:
    from importlib_metadata import version
from pathlib import Path

from . import Nuitka, run_command, Config


class PythonExecutable:
    """
    Wrapper class around Python executable
    """

    def __init__(self, python_path=None, dry_run=False):
        self.exe = python_path if python_path else Path(sys.executable)
        self.dry_run = dry_run
        self.nuitka = Nuitka(nuitka=[os.fspath(self.exe), "-m", "nuitka"])

    @property
    def exe(self):
        return Path(self._exe)

    @exe.setter
    def exe(self, exe):
        self._exe = exe

    @staticmethod
    def is_venv():
        venv = os.environ.get("VIRTUAL_ENV")
        return True if venv else False

    def install(self, packages: list = None):
        for package in packages:
            package_info = package.split('==')
            package_components_len = len(package_info)
            package_name, package_version = None, None
            if package_components_len == 1:
                package_name = package_info[0]
            elif package_components_len == 2:
                package_name = package_info[0]
                package_version = package_info[1]
            else:
                raise ValueError(f"{package} should be of the format 'package_name'=='version'")
            if not self.is_installed(package=package_name):
                logging.info(f"[DEPLOY] Installing package: {package}")
                run_command(
                    command=[self.exe, "-m", "pip", "install", package],
                    dry_run=self.dry_run,
                )
            elif package_version:
                installed_version = version(package_name)
                if package_version != installed_version:
                    logging.info(f"[DEPLOY] Installing package: {package_name}"
                                 f"version: {package_version}")
                    run_command(
                        command=[self.exe, "-m", "pip", "install", "--force", package],
                        dry_run=self.dry_run,
                    )
                else:
                    logging.info(f"[DEPLOY] package: {package_name}=={package_version}"
                                 "already installed")
            else:
                logging.info(f"[DEPLOY] package: {package_name} already installed")

    def is_installed(self, package):
        return bool(util.find_spec(package))

    def create_executable(self, source_file: Path, extra_args: str, config: Config):
        if config.qml_files:
            logging.info(f"[DEPLOY] Included QML files: {config.qml_files}")

        command_str = self.nuitka.create_executable(
                        source_file=source_file,
                        extra_args=extra_args,
                        qml_files=config.qml_files,
                        excluded_qml_plugins=config.excluded_qml_plugins,
                        dry_run=self.dry_run,
                    )

        return command_str
