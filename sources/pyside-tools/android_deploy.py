# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import argparse
import sys
import logging
import shutil
import traceback
from pathlib import Path
from textwrap import dedent

from pkginfo import Wheel

from deploy_lib import (setup_python, get_config, cleanup, install_python_dependencies,
                        config_option_exists, MAJOR_VERSION)
from deploy_lib.android import (create_recipe, extract_and_copy_jar, get_wheel_android_arch,
                                Buildozer, AndroidData, WIDGET_APPLICATION_MODULES,
                                QUICK_APPLICATION_MODULES)


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


    Note: If --ndk-path and --sdk-path are not specified, the defaults from buildozer are used

    Prerequisities: Python main entrypoint file should be named "main.py"

    Platforms Supported: aarch64, armv7a, i686, x86_64

    Supported Modules: Core, Gui, Widgets, Network, OpenGL, Qml, Quick, QuickControls2

    Config file:
        On the first run of the tool, it creates a config file called pysidedeploy.spec which
        controls the various characteristic of the deployment. Users can simply change the value
        in this config file to achieve different properties ie. change the application name,
        deployment platform etc.

        Note: This file is used by both pyside6-deploy and pyside6-android-deploy
"""


def main(name: str = None, pyside_wheel: Path = None, shiboken_wheel: Path = None, ndk_path: Path = None,
         sdk_path: Path = None, config_file: Path = None, init: bool = False,
         loglevel=logging.WARNING, dry_run: bool = False, keep_deployment_files: bool = False,
         force: bool = False):

    logging.basicConfig(level=loglevel)
    main_file = Path.cwd() / "main.py"
    generated_files_path = None
    if not main_file.exists():
        raise RuntimeError(dedent("""
        [DEPLOY] For android deployment to work, the main entrypoint Python file should be named
        'main.py' and it should be run from the application directory
        """))

    # check if ndk and sdk path given, else use default
    if ndk_path and sdk_path:
        logging.warning("[DEPLOY] May not work with custom Ndk and Sdk versions."
                        "Use the default by leaving out --ndk-path and --sdk-path cl"
                        "arguments")

    android_data = AndroidData(wheel_pyside=pyside_wheel, wheel_shiboken=shiboken_wheel,
                               ndk_path=ndk_path, sdk_path=sdk_path)

    python = setup_python(dry_run=dry_run, force=force, init=init)
    config = get_config(python_exe=python.exe, dry_run=dry_run, config_file=config_file,
                        main_file=main_file, android_data=android_data, is_android=True)

    if not config.wheel_pyside and not config.wheel_shiboken:
        raise RuntimeError(f"[DEPLOY] No PySide{MAJOR_VERSION} and Shiboken{MAJOR_VERSION} wheels"
                           "found")

    source_file = config.project_dir / config.source_file
    generated_files_path = source_file.parent / "deployment"
    cleanup(generated_files_path=generated_files_path, config=config, is_android=True)

    install_python_dependencies(config=config, python=python, init=init,
                                packages="android_packages", is_android=True)

    # set application name
    if name:
        config.title = name

    try:
        # create recipes
        # https://python-for-android.readthedocs.io/en/latest/recipes/
        # These recipes are manually added through buildozer.spec file to be used by
        # python_for_android while building the distribution
        if not config.recipes_exist():
            logging.info("[DEPLOY] Creating p4a recipes for PySide6 and shiboken6")
            version = Wheel(config.wheel_pyside).version
            create_recipe(version=version, component=f"PySide{MAJOR_VERSION}",
                          wheel_path=config.wheel_pyside,
                          generated_files_path=generated_files_path)
            create_recipe(version=version, component=f"shiboken{MAJOR_VERSION}",
                          wheel_path=config.wheel_shiboken,
                          generated_files_path=generated_files_path)
            config.recipe_dir = (generated_files_path / "recipes").resolve()

        # extract out and copy .jar files to {generated_files_path}
        if not config.jars_dir or not Path(config.jars_dir).exists():
            logging.info("[DEPLOY] Extract and copy jar files from PySide6 wheel to "
                         f"{generated_files_path}")
            extract_and_copy_jar(wheel_path=config.wheel_pyside,
                                 generated_files_path=generated_files_path)
            config.jars_dir = (generated_files_path / "jar" / "PySide6" / "jar").resolve()

        # check which modules are needed
        # TODO: Optimize this based on the modules needed
        # check if other modules not supported by Android used and raise error
        if not config.modules:
            config.modules = (QUICK_APPLICATION_MODULES if config.qml_files else
                              WIDGET_APPLICATION_MODULES)

        # find architecture from wheel name
        if not config.arch:
            arch = get_wheel_android_arch(wheel=config.wheel_pyside)
            if not arch:
                logging.exception("[DEPLOY] PySide wheel corrupted. Wheel name should end with"
                                  "platform name")
                raise
            config.arch = arch

        # writing config file
        if not dry_run:
            config.update_config()

        if init:
            # config file created above. Exiting.
            logging.info(f"[DEPLOY]: Config file  {config.config_file} created")
            return

        # TODO: include qml files from pysidedeploy.spec rather than from extensions
        # buildozer currently includes all the files with .qml extension

        # init buildozer
        Buildozer.dry_run = dry_run
        logging.info("[DEPLOY] Creating buildozer.spec file")
        Buildozer.initialize(pysidedeploy_config=config)

        # run buildozer
        logging.info("[DEPLOY] Running buildozer deployment")
        Buildozer.create_executable(config.mode)

        # move buildozer build files to {generated_files_path}
        if not dry_run:
            buildozer_build_dir = config.project_dir / ".buildozer"
            if not buildozer_build_dir.exists():
                logging.info(f"[DEPLOY] Unable to copy {buildozer_build_dir} to {generated_files_path}"
                            f"{buildozer_build_dir} does not exist")
            logging.info(f"[DEPLOY] copy {buildozer_build_dir} to {generated_files_path}")
            shutil.move(buildozer_build_dir, generated_files_path)

        logging.info(f"[DEPLOY] apk created in {config.exe_dir}")
    except Exception:
        print(f"Exception occurred: {traceback.format_exc()}")
    finally:
        if generated_files_path and config and not keep_deployment_files:
            cleanup(generated_files_path=generated_files_path, config=config, is_android=True)

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
                        help=("Path to Android Ndk. If omitted, the default from buildozer is used")
                        , required="--sdk-path" in sys.argv)

    parser.add_argument("--sdk-path", type=lambda p: Path(p).resolve(),
                        help=("Path to Android Sdk. If omitted, the default from buildozer is used")
                        , required="--ndk-path" in sys.argv)

    args = parser.parse_args()

    main(args.name, args.wheel_pyside, args.wheel_shiboken, args.ndk_path, args.sdk_path,
         args.config_file, args.init, args.loglevel, args.dry_run, args.keep_deployment_files,
         args.force)
