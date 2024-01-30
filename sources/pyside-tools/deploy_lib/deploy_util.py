# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import ast
import re
import os
import warnings
import logging
import shutil
import sys
from pathlib import Path
from typing import List

from . import EXE_FORMAT, IMPORT_WARNING_PYSIDE
from .config import Config


def config_option_exists():
    for argument in sys.argv:
        if any(item in argument for item in ["--config-file", "-c"]):
            return True

    return False


def cleanup(config: Config, is_android: bool = False):
    """
        Cleanup the generated build folders/files
    """
    if config.generated_files_path.exists():
        shutil.rmtree(config.generated_files_path)
        logging.info("[DEPLOY] Deployment directory purged")

    if is_android:
        buildozer_spec: Path = config.project_dir / "buildozer.spec"
        if buildozer_spec.exists():
            buildozer_spec.unlink()
            logging.info(f"[DEPLOY] {str(buildozer_spec)} removed")

        buildozer_build: Path = config.project_dir / ".buildozer"
        if buildozer_build.exists():
            shutil.rmtree(buildozer_build)
            logging.info(f"[DEPLOY] {str(buildozer_build)} removed")


def create_config_file(dry_run: bool = False, config_file: Path = None, main_file: Path = None):
    """
        Sets up a new pysidedeploy.spec or use an existing config file
    """

    if main_file:
        if main_file.parent != Path.cwd():
            config_file = main_file.parent / "pysidedeploy.spec"
        else:
            config_file = Path.cwd() / "pysidedeploy.spec"

    logging.info(f"[DEPLOY] Creating config file {config_file}")
    if not dry_run:
        shutil.copy(Path(__file__).parent / "default.spec", config_file)

    # the config parser needs a reference to parse. So, in the case of --dry-run
    # use the default.spec file.
    if dry_run:
        config_file = Path(__file__).parent / "default.spec"

    return config_file


def finalize(config: Config):
    """
        Copy the executable into the final location
        For Android deployment, this is done through buildozer
    """
    generated_exec_path = config.generated_files_path / (config.source_file.stem + EXE_FORMAT)
    if generated_exec_path.exists() and config.exe_dir:
        shutil.copy(generated_exec_path, config.exe_dir)
        print("[DEPLOY] Executed file created in "
              f"{str(config.exe_dir / (config.source_file.stem + EXE_FORMAT))}")


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
