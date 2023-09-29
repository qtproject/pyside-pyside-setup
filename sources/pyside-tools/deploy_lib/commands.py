# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import json
import subprocess
import sys
from pathlib import Path
from typing import List

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


def run_qmlimportscanner(qml_files: List[Path], dry_run: bool):
    """
        Runs pyside6-qmlimportscanner to find all the imported qml modules
    """
    if not qml_files:
        return []

    qml_modules = []
    cmd = ["pyside6-qmlimportscanner", "-qmlFiles"]
    cmd.extend([str(qml_file) for qml_file in qml_files])

    if dry_run:
        run_command(command=cmd, dry_run=True)

    # we need to run qmlimportscanner during dry_run as well to complete the
    # command being run by nuitka
    _, json_string = run_command(command=cmd, dry_run=False, fetch_output=True)
    json_string = json_string.decode("utf-8")
    json_array = json.loads(json_string)
    qml_modules = [item['name'] for item in json_array if item['type'] == "module"]
    return qml_modules
