# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

"""pyside6-deploy deployment tool

   How does it work?

   Running "pyside6-deploy path/to/main_file" will
    1. Create a pysidedeploy.spec config file to control the overall deployment process
    2. Prompt the user to create a virtual environment (if not in one already)
       If yes, virtual environment is created in the current folder
       If no, uses the system wide python
    3. Install all dependencies and figure out Qt nuitka optimizations
    2. Use the spec file by android deploy tool or nuitka (desktop), to
       create the executable

   Desktop deployment: Wrapper around Nuitka with support for Windows,
   Linux, Mac
     1. for non-QML cases, only required modules are included
     2. for QML cases, all modules are included because of all QML
        plugins getting included with nuitka

   For other ways of using the tool:
     1. pyside6-deploy (incase main file is called main.py)
     2. pyside6-deploy -c /path/to/config_file
"""

import argparse
import logging
import sys
from pathlib import Path
import shutil
import traceback

from deploy import Config, PythonExecutable

MAJOR_VERSION = 6
EXE_FORMAT = ".exe" if sys.platform == "win32" else ".bin"


def config_option_exists():
    return True if any(item in sys.argv for item in ["--config-file", "-c"]) else False


def main_py_exists():
    return (Path.cwd() / "main.py").exists()


def clean(purge_path: Path):
    """remove the generated deployment files"""
    if purge_path.exists():
        shutil.rmtree(purge_path)
        logging.info("[DEPLOY]: deployment directory purged")
    else:
        print(f"{purge_path} does not exist")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=f"This tool deploys PySide{MAJOR_VERSION} to different platforms",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument("-c", "--config-file", type=str, help="Path to the .spec config file")

    parser.add_argument(
        type=lambda p: Path(p).absolute(),
        help="Path to main python file", nargs="?", dest="main_file",
        default=None if config_option_exists() else Path.cwd() / "main.py")

    parser.add_argument(
        "--init", action="store_true",
        help="Create pysidedeploy.spec file, if it doesn't already exists")

    parser.add_argument(
        "-v", "--verbose", help="run in verbose mode", action="store_const",
        dest="loglevel", const=logging.INFO)

    parser.add_argument("--dry-run", action="store_true", help="show the commands to be run")

    parser.add_argument(
        "--keep-deployment-files",action="store_true",
        help="keep the generated deployment files generated",)

    parser.add_argument("-f", "--force", action="store_true", help="force all input prompts")

    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)
    config_file = Path(args.config_file) if args.config_file else None

    if args.main_file:
        if args.main_file.parent != Path.cwd():
            config_file = args.main_file.parent / "pysidedeploy.spec"
        else:
            config_file = Path.cwd() / "pysidedeploy.spec"

    final_exec_path = None
    config = Config(config_file=config_file)

    # set if available, else fetch from config_file
    source_file = Path(
        config.set_or_fetch(config_property_val=args.main_file, config_property_key="input_file")
    )

    if config.project_dir:
        source_file = config.project_dir / source_file

    generated_files_path = source_file.parent / "deployment"
    if generated_files_path.exists():
        clean(generated_files_path)

    logging.info("[DEPLOY]: Start")

    try:
        python = None
        python_path = config.get_value("python", "python_path")
        if python_path and Path(python_path).exists():
            python = PythonExecutable(Path(python_path), dry_run=args.dry_run)
        else:
            # checking if inside virtual environment
            if not PythonExecutable.is_venv():
                if not args.force:
                    response = input("Not in virtualenv. Do you want to create one? [Y/n]")
                else:
                    response = "no"

                if response.lower() in "yes":
                    # creating new virtual environment
                    python = PythonExecutable(create_venv=True, dry_run=args.dry_run)
                    logging.info("[DEPLOY]: virutalenv created")

            # in venv or user entered no
            if not python:
                python = PythonExecutable(dry_run=args.dry_run)
                logging.info(f"[DEPLOY]: using python at {sys.executable}")

        config.set_value("python", "python_path", str(python.exe))

        if not args.init and not args.dry_run:
            # install packages needed for deployment
            print("[DEPLOY] Installing dependencies \n")
            packages = config.get_value("python", "packages").split(",")
            python.install(packages=packages)
            # nuitka requires patchelf to make patchelf rpath changes for some Qt files
            if sys.platform.startswith("linux"):
                python.install(packages=["patchelf"])

        # identify and set qml files
        config.find_and_set_qml_files()

        if not config.project_dir:
            config.find_and_set_project_dir()

        if config.project_dir == Path.cwd():
            final_exec_path = config.project_dir.relative_to(Path.cwd())
        else:
            final_exec_path = config.project_dir
        final_exec_path = Path(
            config.set_or_fetch(
                config_property_val=final_exec_path, config_property_key="exec_directory"
            )
        ).absolute()

        if not args.dry_run:
            config.update_config()

        if args.init:
            # config file created above. Exiting.
            logging.info(f"[DEPLOY]: Config file  {args.config_file} created")
            sys.exit(0)

        # create executable
        if not args.dry_run:
            print("[DEPLOY] Deploying application")
        python.create_executable(
            source_file=source_file,
            extra_args=config.get_value("nuitka", "extra_args"),
            config=config,
        )
    except Exception:
        print(f"Exception occurred: {traceback.format_exc()}")
    finally:
        # clean up generated deployment files and copy executable into
        # final_exec_path
        if not args.keep_deployment_files and not args.dry_run and not args.init:
            generated_exec_path = generated_files_path / (source_file.stem + EXE_FORMAT)
            if generated_exec_path.exists() and final_exec_path:
                shutil.copy(generated_exec_path, final_exec_path)
                print(
                    f"[DEPLOY] Executed file created in "
                    f"{final_exec_path / (source_file.stem + EXE_FORMAT)}"
                )
            clean(generated_files_path)

    logging.info("[DEPLOY]: End")
