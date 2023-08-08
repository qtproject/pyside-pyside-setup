# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import ast
import logging
import os
import re
import sys
import warnings
from typing import List
from importlib import util
from importlib.metadata import version
from pathlib import Path

from . import Config, Nuitka, run_command

IMPORT_WARNING_PYSIDE = (f"[DEPLOY] Found 'import PySide6' in file {0}"
                         ". Use 'from PySide6 import <module>' or pass the module"
                         " needed using --extra-modules command line argument")


def find_pyside_modules(project_dir: Path, extra_ignore_dirs: List[Path] = None,
                        project_data=None):
    """
    Searches all the python files in the project to find all the PySide modules used by
    the application.
    """
    all_modules = set()
    mod_pattern = re.compile("PySide6.Qt(?P<mod_name>.*)")

    def pyside_imports(py_file: Path):
        modules = []
        contents = py_file.read_text(encoding="utf-8")
        try:
            tree = ast.parse(contents)
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    main_mod_name = node.module
                    if main_mod_name.startswith("PySide6"):
                        if main_mod_name == "PySide6":
                            # considers 'from PySide6 import QtCore'
                            for imported_module in node.names:
                                full_mod_name = imported_module.name
                                if full_mod_name.startswith("Qt"):
                                    modules.append(full_mod_name[2:])
                            continue

                        # considers 'from PySide6.QtCore import Qt'
                        match = mod_pattern.search(main_mod_name)
                        if match:
                            mod_name = match.group("mod_name")
                            modules.append(mod_name)
                        else:
                            logging.warning((
                                f"[DEPLOY] Unable to find module name from{ast.dump(node)}"))

                if isinstance(node, ast.Import):
                    for imported_module in node.names:
                        full_mod_name = imported_module.name
                        if full_mod_name == "PySide6":
                            logging.warning(IMPORT_WARNING_PYSIDE.format(str(py_file)))
        except Exception as e:
            raise RuntimeError(f"[DEPLOY] Finding module import failed on file {str(py_file)} with "
                               f"error {e}")

        return set(modules)

    py_candidates = []
    ignore_dirs = ["__pycache__", "env", "venv", "deployment"]

    if project_data:
        py_candidates = project_data.python_files
        ui_candidates = project_data.ui_files
        qrc_candidates = project_data.qrc_files
        ui_py_candidates = None
        qrc_ui_candidates = None

        if ui_candidates:
            ui_py_candidates = [(file.parent / f"ui_{file.stem}.py") for file in ui_candidates
                                if (file.parent / f"ui_{file.stem}.py").exists()]

            if len(ui_py_candidates) != len(ui_candidates):
                warnings.warn("[DEPLOY] The number of uic files and their corresponding Python"
                              " files don't match.", category=RuntimeWarning)

            py_candidates.extend(ui_py_candidates)

        if qrc_candidates:
            qrc_ui_candidates = [(file.parent / f"rc_{file.stem}.py") for file in qrc_candidates
                                 if (file.parent / f"rc_{file.stem}.py").exists()]

            if len(qrc_ui_candidates) != len(qrc_candidates):
                warnings.warn("[DEPLOY] The number of qrc files and their corresponding Python"
                              " files don't match.", category=RuntimeWarning)

            py_candidates.extend(qrc_ui_candidates)

        for py_candidate in py_candidates:
            all_modules = all_modules.union(pyside_imports(py_candidate))
        return list(all_modules)

    # incase there is not .pyproject file, search all python files in project_dir, except
    # ignore_dirs
    if extra_ignore_dirs:
        ignore_dirs.extend(extra_ignore_dirs)

    # find relevant .py files
    _walk = os.walk(project_dir)
    for root, dirs, files in _walk:
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith(".")]
        for py_file in files:
            if py_file.endswith(".py"):
                py_candidates.append(Path(root) / py_file)

    for py_candidate in py_candidates:
        all_modules = all_modules.union(pyside_imports(py_candidate))

    if not all_modules:
        ValueError("[DEPLOY] No PySide6 modules were found")

    return list(all_modules)


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

    def is_pyenv_python(self):
        pyenv_root = os.environ.get("PYENV_ROOT")

        if pyenv_root:
            resolved_exe = self.exe.resolve()
            if str(resolved_exe).startswith(pyenv_root):
                return True

        return False

    def install(self, packages: list = None):
        _, installed_packages = run_command(command=[str(self.exe), "-m", "pip", "freeze"], dry_run=False
                                            , fetch_output=True)
        installed_packages = [p.decode().split('==')[0] for p in installed_packages.split()]
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
            if (package_name not in installed_packages) and (not self.is_installed(package_name)):
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
                                 " already installed")
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
