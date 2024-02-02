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

from deploy_lib import (MAJOR_VERSION, DesktopConfig, cleanup, config_option_exists,
                        finalize, create_config_file, PythonExecutable, Nuitka,
                        HELP_EXTRA_MODULES, HELP_EXTRA_IGNORE_DIRS)


TOOL_DESCRIPTION = dedent(f"""
                          This tool deploys PySide{MAJOR_VERSION} to desktop (Windows, Linux,
                          macOS) platforms. The following types of executables are produced as per
                          the platform:

                          Windows = .exe
                          macOS = .app
                          Linux = .bin
                          """)


def main(main_file: Path = None, name: str = None, config_file: Path = None, init: bool = False,
         loglevel=logging.WARNING, dry_run: bool = False, keep_deployment_files: bool = False,
         force: bool = False, extra_ignore_dirs: str = None, extra_modules_grouped: str = None):

    logging.basicConfig(level=loglevel)
    if config_file and not config_file.exists() and not main_file.exists():
        raise RuntimeError(dedent("""
            Directory does not contain main.py file.
            Please specify the main python entrypoint file or the config file.
            Run "pyside6-deploy desktop --help" to see info about cli options.

            pyside6-deploy exiting..."""))

    # Nuitka command to run
    command_str = None
    config = None
    logging.info("[DEPLOY] Start")

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

    python = PythonExecutable(dry_run=dry_run, init=init, force=force)
    config_file_exists = config_file and Path(config_file).exists()

    if config_file_exists:
        logging.info(f"[DEPLOY] Using existing config file {config_file}")
    else:
        config_file = create_config_file(dry_run=dry_run, config_file=config_file,
                                         main_file=main_file)

    config = DesktopConfig(config_file=config_file, source_file=main_file, python_exe=python.exe,
                           dry_run=dry_run, existing_config_file=config_file_exists,
                           extra_ignore_dirs=extra_ignore_dirs)

    # set application name
    if name:
        config.title = name

    cleanup(config=config)

    python.install_dependencies(config=config, packages="packages")

    # required by Nuitka for pyenv Python
    add_arg = " --static-libpython=no"
    if python.is_pyenv_python() and add_arg not in config.extra_args:
        config.extra_args += add_arg

    config.modules += list(set(extra_modules).difference(set(config.modules)))

    # writing config file
    # in the case of --dry-run, we use default.spec as reference. Do not save the changes
    # for --dry-run
    if not dry_run:
        config.update_config()

    if config.qml_files:
        logging.info(f"[DEPLOY] Included QML files: {config.qml_files}")

    if init:
        # config file created above. Exiting.
        logging.info(f"[DEPLOY]: Config file {config.config_file} created")
        return

    try:
        # create executable
        if not dry_run:
            logging.info("[DEPLOY] Deploying application")

        nuitka = Nuitka(nuitka=[python.exe, "-m", "nuitka"])
        command_str = nuitka.create_executable(source_file=config.source_file,
                                               extra_args=config.extra_args,
                                               qml_files=config.qml_files,
                                               qt_plugins=config.qt_plugins,
                                               excluded_qml_plugins=config.excluded_qml_plugins,
                                               icon=config.icon,
                                               dry_run=dry_run,
                                               permissions=config.permissions)
    except Exception:
        print(f"[DEPLOY] Exception occurred: {traceback.format_exc()}")
    finally:
        if config.generated_files_path and config:
            finalize(config=config)
            if not keep_deployment_files:
                cleanup(config=config)

    logging.info("[DEPLOY] End")
    return command_str


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=TOOL_DESCRIPTION)

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

    parser.add_argument("--extra-ignore-dirs", type=str, help=HELP_EXTRA_IGNORE_DIRS)

    parser.add_argument("--extra-modules", type=str, help=HELP_EXTRA_MODULES)

    args = parser.parse_args()

    main(args.main_file, args.name, args.config_file, args.init, args.loglevel, args.dry_run,
         args.keep_deployment_files, args.force, args.extra_ignore_dirs, args.extra_modules)
