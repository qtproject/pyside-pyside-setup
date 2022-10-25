# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import sys
import os
import logging
from importlib import util
from pathlib import Path

from . import Nuitka, run_command, Config


class PythonExecutable:
    """
    Wrapper class around Python executable
    """

    def __init__(self, python_path=None, create_venv=False, dry_run=False):
        self.exe = python_path if python_path else Path(sys.executable)
        self.dry_run = dry_run
        if create_venv:
            self.__create_venv()

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

    def __create_venv(self):
        self.install("virtualenv")
        if not self.is_venv():
            run_command(
                command=[self.exe, "-m", "venv", Path.cwd() / "deployment" / "venv"],
                dry_run=self.dry_run,
            )
            venv_path = Path(os.environ["VIRTUAL_ENV"])
            if sys.platform == "win32":
                self.exe = venv_path / "Scripts" / "python.exe"
            elif sys.platform in ["linux", "darwin"]:
                self.exe = venv_path / "bin" / "python"
        else:
            logging.info("[DEPLOY]: You are already in virtual environment!")

    def install(self, packages: list = None):
        if packages:
            for package in packages:
                if not self.is_installed(package=package):
                    logging.info(f"[DEPLOY]: Installing package: {package}")
                    run_command(
                        command=[self.exe, "-m", "pip", "install", package],
                        dry_run=self.dry_run,
                    )
                else:
                    logging.info(f"[DEPLOY]: Upgrading package: {package}")
                    run_command(
                        command=[self.exe, "-m", "pip", "install", "--upgrade", package],
                        dry_run=self.dry_run,
                    )

    def is_installed(self, package):
        return bool(util.find_spec(package))

    def create_executable(self, source_file: Path, extra_args: str, config: Config):
        if config.qml_files:
            logging.info(f"[DEPLOY]: Included QML files: {config.qml_files}")

        self.nuitka.create_executable(
            source_file=source_file,
            extra_args=extra_args,
            qml_files=config.qml_files,
            dry_run=self.dry_run,
        )

