# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import json
import subprocess
import sys
import shutil
import tempfile
from pathlib import Path
from functools import lru_cache


"""
All utility functions for deployment
"""


def run_command(command, dry_run: bool, fetch_output: bool = False):
    command_str = " ".join([str(cmd) for cmd in command])
    output = None
    is_windows = (sys.platform == "win32")
    try:
        if not dry_run:
            if fetch_output:
                output = subprocess.check_output(command, shell=is_windows)
            else:
                subprocess.check_call(command, shell=is_windows)
        else:
            print(command_str + "\n")
    except FileNotFoundError as error:
        raise FileNotFoundError(f"[DEPLOY] {error.filename} not found")
    except subprocess.CalledProcessError as error:
        raise RuntimeError(
            f"[DEPLOY] Command {command_str} failed with error {error} and return_code"
            f"{error.returncode}"
        )
    except Exception as error:
        raise RuntimeError(f"[DEPLOY] Command {command_str} failed with error {error}")

    return command_str, output


@lru_cache
def run_qmlimportscanner(qml_files: tuple[Path], dry_run: bool):
    """
        Runs pyside6-qmlimportscanner to find all the imported qml modules in project_dir
    """
    qml_modules = []
    # Create a temporary directory to copy all the .qml_files
    # TODO: Modify qmlimportscanner code in qtdeclarative to include a flag to ignore directories
    # Then, this copy into a temporary directory can be avoided
    # See 36b425ea8bf36d47694ea69fa7d129b6d5a2ca2d in gerrit
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        # Copy only files with .qml suffix
        for qml_file in qml_files:
            if qml_file.suffix == ".qml":
                shutil.copy2(qml_file.resolve(), temp_path / qml_file.name)

        cmd = ["pyside6-qmlimportscanner", "-rootPath", str(temp_path)]

        if dry_run:
            run_command(command=cmd, dry_run=True)

        # Run qmlimportscanner during dry_run as well to complete the command being run by nuitka
        _, json_string = run_command(command=cmd, dry_run=False, fetch_output=True)
        json_string = json_string.decode("utf-8")
        json_array = json.loads(json_string)
        qml_modules = [item['name'] for item in json_array if item['type'] == "module"]

    return qml_modules
