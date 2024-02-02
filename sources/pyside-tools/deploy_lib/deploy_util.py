# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import logging
import shutil
import sys
from pathlib import Path

from . import EXE_FORMAT
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
        if sys.platform == "darwin":
            shutil.copytree(generated_exec_path, config.exe_dir / (config.title + EXE_FORMAT),
                            dirs_exist_ok=True)
        else:
            shutil.copy(generated_exec_path, config.exe_dir)
        print("[DEPLOY] Executed file created in "
              f"{str(config.exe_dir / (config.source_file.stem + EXE_FORMAT))}")
