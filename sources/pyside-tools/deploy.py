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

import configparser
import subprocess
import argparse
import logging
import sys
import os
from pathlib import Path
from configparser import ConfigParser
import shutil
from importlib import util
import traceback

MAJOR_VERSION = 6
EXE_FORMAT = ".exe" if sys.platform == "win32" else ".bin"


def run_command(command, dry_run: bool):
    command_str = " ".join([str(cmd) for cmd in command])
    try:
        if not dry_run:
            subprocess.check_call(command, shell=(sys.platform == "win32"))
        else:
            print(command_str + "\n")
    except FileNotFoundError as error:
        logging.exception(f"[DEPLOY]: {error.filename} not found")
        raise
    except subprocess.CalledProcessError as error:
        logging.exception(
             f"[DEPLOY]: Command {command_str} failed with error {error} and return_code"
             f"{error.returncode}"
        )
        raise
    except Exception as error:
        logging.exception(f"[DEPLOY]: Command {command_str} failed with error {error}")
        raise


class Nuitka:
    """
    Wrapper class around the nuitka executable, enabling its usage through python code
    """

    def __init__(self, nuitka):
        self.nuitka = nuitka

    def create_executable(
        self, source_file: Path, extra_args: str, qml_files: list[Path], dry_run: bool
    ):
        extra_args = extra_args.split()
        qml_args = []
        if qml_files:
            # this includes "all" the plugins
            # FIXME: adding the "qml" plugin is equivalent to "all" because of dependencies
            # Ideally it should only add the specific qml plugins. eg: quick window, quick controls
            qml_args.append("--include-qt-plugins=all")
            qml_args.extend(
                [f"--include-data-files={qml_file}=./{qml_file.name}" for qml_file in qml_files]
            )

        output_dir = source_file.parent / "deployment"
        if not dry_run:
            output_dir.mkdir(parents=True, exist_ok=True)
            print("[DEPLOY] Running Nuitka")
        command = self.nuitka + [
            source_file,
            "--follow-imports",
            "--onefile",
            "--enable-plugin=pyside6",
            f"--output-dir={output_dir}",
        ]
        command.extend(extra_args + qml_args)

        if sys.platform == "linux":
            linux_icon = str(Path(__file__).parent / "deploy" / "pyside_icon.jpg")
            command.append(f"--linux-onefile-icon={linux_icon}")

        run_command(command=command, dry_run=dry_run)


class Config:
    """
    Wrapper class around config file, whose options are used to control the executable creation
    """

    def __init__(self, config_file: Path) -> None:
        self.config_file = config_file
        self.parser = ConfigParser(comment_prefixes="/", allow_no_value=True)
        if not self.config_file.exists():
            logging.info(f"[DEPLOY]: Creating config file {self.config_file}")
            shutil.copy(Path(__file__).parent / "deploy" / "default.spec", self.config_file)
        else:
            print(f"Using existing config file {config_file}")
        self.parser.read(self.config_file)

        self.project_dir = None
        if self.get_value("app", "project_dir"):
            self.project_dir = Path(self.get_value("app", "project_dir")).absolute()

        self.qml_files = []
        config_qml_files = self.get_value("qt", "qml_files")
        if config_qml_files and self.project_dir:
            self.qml_files = [Path(self.project_dir) / file for file in config_qml_files.split(",")]

    def update_config(self):
        logging.info("[DEPLOY] Creating {config_file}")
        with open(self.config_file, "w+") as config_file:
            self.parser.write(config_file, space_around_delimiters=True)

    def set_value(self, section: str, key: str, new_value: str):
        try:
            current_value = self.get_value(section, key)
            if current_value != new_value:
                self.parser.set(section, key, new_value)
        except configparser.NoOptionError:
            logging.warning(f"[DEPLOY]: key {key} does not exist")
        except configparser.NoSectionError:
            logging.warning(f"[DEPLOY]: section {section} does not exist")

    def get_value(self, section: str, key: str):
        try:
            return self.parser.get(section, key)
        except configparser.NoOptionError:
            logging.warning(f"[DEPLOY]: key {key} does not exist")
        except configparser.NoSectionError:
            logging.warning(f"[DEPLOY]: section {section} does not exist")

    def set_or_fetch(self, config_property_val, config_property_key, config_property_group="app"):
        """
        Write to config_file if 'config_property_key' is known without config_file
        Fetch and return from config_file if 'config_property_key' is unknown, but
        config_file exists
        Otherwise, raise an exception
        """
        if config_property_val:
            self.set_value(config_property_group, config_property_key, str(config_property_val))
            return config_property_val
        elif self.get_value(config_property_group, config_property_key):
            return self.get_value(config_property_group, config_property_key)
        else:
            logging.exception(
                f"[DEPLOY]: No {config_property_key} specified in config file or as cli option"
            )
            raise

    @property
    def qml_files(self):
        return self._qml_files

    @qml_files.setter
    def qml_files(self, qml_files):
        self._qml_files = qml_files

    @property
    def project_dir(self):
        return self._project_dir

    @project_dir.setter
    def project_dir(self, project_dir):
        self._project_dir = project_dir

    def find_and_set_qml_files(self):
        """Fetches all the qml_files in the folder and sets them if the
        field qml_files is empty in the config_dir"""

        if self.project_dir:
            qml_files_str = self.get_value("qt", "qml_files")
            self.qml_files = []
            for file in qml_files_str.split(","):
                if file:
                    self.qml_files.append(Path(self.project_dir) / file)
        else:
            qml_files_temp = None
            source_file = (
                Path(self.get_value("app", "input_file"))
                if self.get_value("app", "input_file")
                else None
            )
            python_exe = (
                Path(self.get_value("python", "python_path"))
                if self.get_value("python", "python_path")
                else None
            )
            if source_file and python_exe:
                if not self.qml_files:
                    qml_files_temp = list(source_file.parent.glob("**/*.qml"))

                # add all QML files, excluding the ones shipped with installed PySide6
                # The QML files shipped with PySide6 gets added if venv is used,
                # because of recursive glob
                if python_exe.parent.parent == source_file.parent:
                    # python venv path is inside the main source dir
                    qml_files_temp = list(
                        set(qml_files_temp) - set(python_exe.parent.parent.rglob("*.qml"))
                    )

                if len(qml_files_temp) > 500:
                    if "site-packages" in str(qml_files_temp[-1]):
                        logging.warning(
                            "You seem to include a lot of QML files from a \
                                            local virtual env. Are they intended?"
                        )
                    else:
                        logging.warning(
                            "You seem to include a lot of QML files. \
                                        Are they intended?"
                        )

                if qml_files_temp:
                    extra_qml_files = [Path(file) for file in qml_files_temp]
                    self.qml_files.extend(extra_qml_files)
                    self.set_value(
                        "qt", "qml_files", ",".join([str(file) for file in self.qml_files])
                    )
                    logging.info("[DEPLOY] QML files identified and set in config_file")

    def find_and_set_project_dir(self):
        source_file = (
            Path(self.get_value("app", "input_file"))
            if self.get_value("app", "input_file")
            else None
        )

        if self.qml_files:
            paths = self.qml_files.copy()
            paths.append(source_file.absolute())
            self.project_dir = Path(os.path.commonpath(paths=paths))

            # update all qml paths
            logging.info("[DEPLOY] Update QML files paths to relative paths")
            qml_relative_paths = ",".join(
                [str(qml_file.relative_to(self.project_dir)) for qml_file in self.qml_files]
            )
            self.set_value("qt", "qml_files", qml_relative_paths)
        else:
            self.project_dir = source_file.parent

        # update input_file path
        logging.info("[DEPLOY] Update input_file path")
        self.set_value("app", "input_file", str(source_file.relative_to(self.project_dir)))

        logging.info("[DEPLOY] Update project_dir path")
        if self.project_dir != Path.cwd():
            self.set_value("app", "project_dir", str(self.project_dir))
        else:
            self.set_value("app", "project_dir", str(self.project_dir.relative_to(Path.cwd())))


class PythonExecutable:
    """
    Wrapper class around Python executable
    """

    def __init__(self, python_path=None, create_venv=False, dry_run=False):
        self.exe = python_path if python_path else Path(sys.executable)
        self.dry_run = dry_run
        if create_venv:
            self.__create_venv()
        self.nuitka = Nuitka(nuitka=[self.exe, "-m", "nuitka"])

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
