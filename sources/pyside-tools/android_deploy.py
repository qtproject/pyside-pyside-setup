# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

import sys
import argparse
import logging
import shutil
import traceback
from pathlib import Path
from textwrap import dedent

from deploy_lib import (create_config_file, cleanup, config_option_exists, PythonExecutable,
                        MAJOR_VERSION, HELP_EXTRA_IGNORE_DIRS, HELP_EXTRA_MODULES)
from deploy_lib.android import AndroidData, AndroidConfig
from deploy_lib.android.buildozer import Buildozer


""" pyside6-android-deploy deployment tool

    Deployment tool that uses buildozer (https://buildozer.readthedocs.io/en/latest/) and
    python-for-android (https://python-for-android.readthedocs.io/en/latest/) to deploy PySide6
    applications to Android

    How does it work?

    Command: pyside6-android-deploy --wheel-pyside=<pyside_wheel_path>
                                    --wheel-shiboken=<shiboken_wheel_path>
                                    --ndk-path=<optional_ndk_path>
                                    --sdk-path=<optional_sdk_path>
             pyside6-android-deploy android -c /path/to/pysidedeploy.spec


    Note: If --ndk-path and --sdk-path are not specified, the cache of the tool
    `.pyside6_android_deploy` is checked in the user's HOME directory. If it is not found, the user
    will have to manually download them.

    Prerequisities: Python main entrypoint file should be named "main.py"

    Platforms Supported: aarch64, armv7a, i686, x86_64

    Config file:
        On the first run of the tool, it creates a config file called pysidedeploy.spec which
        controls the various characteristic of the deployment. Users can simply change the value
        in this config file to achieve different properties ie. change the application name,
        deployment platform etc.

        Note: This file is used by both pyside6-deploy and pyside6-android-deploy
"""


def main(name: str = None, pyside_wheel: Path = None, shiboken_wheel: Path = None,
         ndk_path: Path = None, sdk_path: Path = None, config_file: Path = None, init: bool = False,
         loglevel=logging.WARNING, dry_run: bool = False, keep_deployment_files: bool = False,
         force: bool = False, extra_ignore_dirs: str = None, extra_modules_grouped: str = None):

    logging.basicConfig(level=loglevel)

    if extra_ignore_dirs:
        extra_ignore_dirs = extra_ignore_dirs.split(",")

    extra_modules = []
    if extra_modules_grouped:
        tmp_extra_modules = extra_modules_grouped.split(",")
        for extra_module in tmp_extra_modules:
            if extra_module.startswith("Qt"):
                extra_modules.append(extra_module[2:])
            else:
                extra_modules.append(extra_module)

    main_file = Path.cwd() / "main.py"
    if not main_file.exists():
        raise RuntimeError(("[DEPLOY] For Android deployment to work, the main"
                            " entrypoint Python file should be named 'main.py'"
                            " and it should be run from the application"
                            " directory"))

    android_data = AndroidData(wheel_pyside=pyside_wheel, wheel_shiboken=shiboken_wheel,
                               ndk_path=ndk_path, sdk_path=sdk_path)

    python = PythonExecutable(dry_run=dry_run, init=init, force=force)

    config_file_exists = config_file and Path(config_file).exists()

    if config_file_exists:
        logging.info(f"[DEPLOY] Using existing config file {config_file}")
    else:
        config_file = create_config_file(main_file=main_file, dry_run=dry_run)

    config = AndroidConfig(config_file=config_file, source_file=main_file,
                           python_exe=python.exe, dry_run=dry_run, android_data=android_data,
                           existing_config_file=config_file_exists,
                           extra_ignore_dirs=extra_ignore_dirs, name=name)

    if not config.wheel_pyside and not config.wheel_shiboken:
        raise RuntimeError(f"[DEPLOY] No PySide{MAJOR_VERSION} and Shiboken{MAJOR_VERSION} wheels"
                           "found")

    cleanup(config=config, is_android=True)

    python.install_dependencies(config=config, packages="android_packages", is_android=True)

    try:
        config.modules += list(set(extra_modules).difference(set(config.modules)))

        # this cannot be done when config file is initialized because cleanup() removes it
        # so this can only be done after the cleanup()
        config.jars_dir = config.find_jars_dir()
        config.recipe_dir = config.find_recipe_dir()

        # TODO: include qml files from pysidedeploy.spec rather than from extensions
        # buildozer currently includes all the files with .qml extension

        # init buildozer
        Buildozer.dry_run = dry_run
        logging.info("[DEPLOY] Creating buildozer.spec file")
        Buildozer.initialize(pysidedeploy_config=config)

        # writing config file
        if not dry_run:
            config.update_config()

        if init:
            # config file created above. Exiting.
            logging.info(f"[DEPLOY]: Config file  {config.config_file} created")
            return

        # run buildozer
        logging.info("[DEPLOY] Running buildozer deployment")
        Buildozer.create_executable(config.mode)

        # move buildozer build files to {generated_files_path}
        if not dry_run:
            buildozer_build_dir = config.project_dir / ".buildozer"
            if not buildozer_build_dir.exists():
                logging.info(f"[DEPLOY] Unable to copy {buildozer_build_dir} to "
                             f"{config.generated_files_path}. {buildozer_build_dir} does not exist")
            logging.info(f"[DEPLOY] copy {buildozer_build_dir} to {config.generated_files_path}")
            shutil.move(buildozer_build_dir, config.generated_files_path)

        logging.info(f"[DEPLOY] apk created in {config.exe_dir}")
    except Exception:
        print(f"Exception occurred: {traceback.format_exc()}")
    finally:
        if config.generated_files_path and config and not keep_deployment_files:
            cleanup(config=config, is_android=True)

    logging.info("[DEPLOY] End")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=dedent(f"""
                           This tool deploys PySide{MAJOR_VERSION} to Android platforms.

                           Note: The main python entrypoint should be named main.py
                           """),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument("-c", "--config-file", type=lambda p: Path(p).absolute(),
                        default=(Path.cwd() / "pysidedeploy.spec"),
                        help="Path to the .spec config file")

    parser.add_argument(
        "--init", action="store_true",
        help="Create pysidedeploy.spec file, if it doesn't already exists")

    parser.add_argument(
        "-v", "--verbose", help="run in verbose mode", action="store_const",
        dest="loglevel", const=logging.INFO)

    parser.add_argument("--dry-run", action="store_true", help="show the commands to be run")

    parser.add_argument("--keep-deployment-files", action="store_true",
                        help="keep the generated deployment files generated")

    parser.add_argument("-f", "--force", action="store_true", help="force all input prompts")

    parser.add_argument("--name", type=str, help="Application name")

    parser.add_argument("--wheel-pyside", type=lambda p: Path(p).resolve(),
                        help=f"Path to PySide{MAJOR_VERSION} Android Wheel",
                        required=not config_option_exists())

    parser.add_argument("--wheel-shiboken", type=lambda p: Path(p).resolve(),
                        help=f"Path to shiboken{MAJOR_VERSION} Android Wheel",
                        required=not config_option_exists())

    parser.add_argument("--ndk-path", type=lambda p: Path(p).resolve(),
                        help=("Path to Android NDK. The required version is r26b."
                              "If not provided, the tool will check its cache at "
                              ".pyside6_android_deploy to find the NDK.")
                        )

    parser.add_argument("--sdk-path", type=lambda p: Path(p).resolve(),
                        help=("Path to Android SDK. If omitted, the tool's cache at "
                              ".pyside6_android_deploy is checked to find the SDK. Otherwise "
                              "the default from buildozer is used.")
                        )

    parser.add_argument("--extra-ignore-dirs", type=str, help=HELP_EXTRA_IGNORE_DIRS)

    parser.add_argument("--extra-modules", type=str, help=HELP_EXTRA_MODULES)

    args = parser.parse_args()

    # check if the Python version is greater than 3.12
    if sys.version_info >= (3, 12):
        raise RuntimeError("[DEPLOY] Android deployment requires Python version 3.11 or lower. "
                           "This is due to a restriction in buildozer.")

    main(args.name, args.wheel_pyside, args.wheel_shiboken, args.ndk_path, args.sdk_path,
         args.config_file, args.init, args.loglevel, args.dry_run, args.keep_deployment_files,
         args.force, args.extra_ignore_dirs, args.extra_modules)
