# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

""" pyside6-deploy deployment tool

    Deployment tool that uses Nuitka to deploy PySide6 applications to various desktop (Windows,
    Linux, macOS) platforms.

    How does it work?

    Command: pyside6-deploy path/to/main_file
             pyside6-deploy (incase main file is called main.py)
             pyside6-deploy -c /path/to/config_file

    Platforms supported: Linux, Windows, macOS
    Module binary inclusion:
        1. for non-QML cases, only required modules are included
        2. for QML cases, all modules are included because of all QML plugins getting included
            with nuitka

    Config file:
        On the first run of the tool, it creates a config file called pysidedeploy.spec which
        controls the various characteristic of the deployment. Users can simply change the value
        in this config file to achieve different properties ie. change the application name,
        deployment platform etc.

        Note: This file is used by both pyside6-deploy and pyside6-android-deploy

"""

import argparse
import logging
import traceback
from pathlib import Path
from textwrap import dedent

from deploy_lib import (MAJOR_VERSION, Config, cleanup, config_option_exists,
                        finalize, get_config, install_python_dependencies,
                        setup_python)


def main(main_file: Path = None, name: str = None, config_file: Path = None, init: bool = False,
         loglevel=logging.WARNING, dry_run: bool = False, keep_deployment_files: bool = False,
         force: bool = False):

    logging.basicConfig(level=loglevel)
    if config_file and not config_file.exists() and not main_file.exists():
        raise RuntimeError(dedent("""
            Directory does not contain main.py file.
            Please specify the main python entrypoint file or the config file.
            Run "pyside6-deploy desktop --help" to see info about cli options.

            pyside6-deploy exiting..."""))

    # Nuitka command to run
    command_str = None
    generated_files_path = None
    config = None
    logging.info("[DEPLOY] Start")

    python = setup_python(dry_run=dry_run, force=force, init=init)
    config = get_config(python_exe=python.exe, dry_run=dry_run, config_file=config_file,
                        main_file=main_file)

    # set application name
    if name:
        config.title = name

    source_file = config.project_dir / config.source_file

    generated_files_path = source_file.parent / "deployment"
    cleanup(generated_files_path=generated_files_path, config=config)

    install_python_dependencies(config=config, python=python, init=init,
                                packages="packages")

    # required by Nuitka for pyenv Python
    if python.is_pyenv_python():
        config.extra_args += " --static-libpython=no"

    # writing config file
    # in the case of --dry-run, we use default.spec as reference. Do not save the changes
    # for --dry-run
    if not dry_run:
        config.update_config()

    if init:
        # config file created above. Exiting.
        logging.info(f"[DEPLOY]: Config file {config.config_file} created")
        return

    try:
        # create executable
        if not dry_run:
            logging.info("[DEPLOY] Deploying application")

        command_str = python.create_executable(
                        source_file=source_file,
                        extra_args=config.extra_args,
                        config=config,
                    )
    except Exception:
        print(f"[DEPLOY] Exception occurred: {traceback.format_exc()}")
    finally:
        if generated_files_path and config:
            finalize(generated_files_path=generated_files_path, config=config)
            if not keep_deployment_files:
                cleanup(generated_files_path=generated_files_path, config=Config)

    logging.info("[DEPLOY] End")
    return command_str


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(f"This tool deploys PySide{MAJOR_VERSION} to desktop (Windows, Linux, macOS)"
                     "platforms"),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument("-c", "--config-file", type=lambda p: Path(p).absolute(),
                        default=(Path.cwd() / "pysidedeploy.spec"),
                        help="Path to the .spec config file")

    parser.add_argument(
        type=lambda p: Path(p).absolute(),
        help="Path to main python file", nargs="?", dest="main_file",
        default=None if config_option_exists() else Path.cwd() / "main.py")

    parser.add_argument(
        "--init", action="store_true",
        help="Create pysidedeploy.spec file, if it doesn't already exists")

    parser.add_argument(
        "-v", "--verbose", help="Run in verbose mode", action="store_const",
        dest="loglevel", const=logging.INFO)

    parser.add_argument("--dry-run", action="store_true", help="Show the commands to be run")

    parser.add_argument(
        "--keep-deployment-files", action="store_true",
        help="Keep the generated deployment files generated")

    parser.add_argument("-f", "--force", action="store_true", help="Force all input prompts")

    parser.add_argument("--name", type=str, help="Application name")

    args = parser.parse_args()

    main(args.main_file, args.name, args.config_file, args.init, args.loglevel, args.dry_run,
         args.keep_deployment_files, args.force)
