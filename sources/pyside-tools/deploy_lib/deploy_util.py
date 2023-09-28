# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import sys
import logging
import shutil

from pathlib import Path
from .config import Config
from .python_helper import PythonExecutable
from . import EXE_FORMAT


def config_option_exists():
    for argument in sys.argv:
        if any(item in argument for item in ["--config-file", "-c"]):
            return True

    return False


def cleanup(generated_files_path: Path, config: Config, is_android: bool = False):
    """
        Cleanup the generated build folders/files
    """
    if generated_files_path.exists():
        shutil.rmtree(generated_files_path)
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


def get_config(python_exe: Path, dry_run: bool = False, config_file: Path = None, main_file:
               Path = None, android_data=None, is_android: bool = False):
    """
        Sets up a new pysidedeploy.spec or use an existing config file
    """

    config_file_exists = config_file and Path(config_file).exists()

    if main_file and not config_file_exists:
        if main_file.parent != Path.cwd():
            config_file = main_file.parent / "pysidedeploy.spec"
        else:
            config_file = Path.cwd() / "pysidedeploy.spec"

    if config_file_exists:
        logging.info(f"[DEPLOY] Using existing config file {config_file}")
    else:
        logging.info(f"[DEPLOY] Creating config file {config_file}")
        if not dry_run:
            shutil.copy(Path(__file__).parent / "default.spec", config_file)

    # the config parser needs a reference to parse. So, in the case of --dry-run
    # use the default.spec file.
    if dry_run and not config_file_exists:
        config_file = Path(__file__).parent / "default.spec"

    config = Config(config_file=config_file, source_file=main_file, python_exe=python_exe,
                    dry_run=dry_run, android_data=android_data, is_android=is_android,
                    existing_config_file=config_file_exists)

    return config


def setup_python(dry_run: bool, force: bool, init: bool):
    """
        Sets up Python venv for deployment, and return a wrapper around the venv environment
    """
    python = None
    response = "yes"
    # checking if inside virtual environment
    if not PythonExecutable.is_venv() and not force and not dry_run and not init:
        response = input(("You are not using a virtual environment. pyside6-deploy needs to install"
                          " a few Python packages for deployment to work seamlessly. \n"
                          "Proceed? [Y/n]"))

    if response.lower() in ["no", "n"]:
        print("[DEPLOY] Exiting ...")
        sys.exit(0)

    python = PythonExecutable(dry_run=dry_run)
    logging.info(f"[DEPLOY] Using python at {sys.executable}")

    return python


def install_python_dependencies(config: Config, python: PythonExecutable, init: bool,
                                packages: str, is_android: bool = False):
    """
        Installs the python package dependencies for the target deployment platform
    """
    if not init:
        # install packages needed for deployment
        logging.info("[DEPLOY] Installing dependencies")
        packages = config.get_value("python", packages).split(",")
        python.install(packages=packages)
        # nuitka requires patchelf to make patchelf rpath changes for some Qt files
        if sys.platform.startswith("linux") and not is_android:
            python.install(packages=["patchelf"])


def finalize(generated_files_path: Path, config: Config):
    """
        Copy the executable into the final location
        For Android deployment, this is done through buildozer
    """
    generated_exec_path = generated_files_path / (config.source_file.stem + EXE_FORMAT)
    if generated_exec_path.exists() and config.exe_dir:
        shutil.copy(generated_exec_path, config.exe_dir)
        print("[DEPLOY] Executed file created in "
              f"{str(config.exe_dir / (config.source_file.stem + EXE_FORMAT))}")
