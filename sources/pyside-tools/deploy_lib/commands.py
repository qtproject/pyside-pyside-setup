# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
# Qt-Security score:critical reason:execute-external-code
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from functools import cache
from . import DEFAULT_IGNORE_DIRS


"""
All utility functions for deployment
"""


def run_command(command, dry_run: bool, fetch_output: bool = False):
    command_str = " ".join([str(cmd) for cmd in command])
    output = None

    # Resolve the full path to the executable to help prevent command injection.
    # shell=True is avoided because it passes the command through a shell interpreter,
    # enabling injection when unsanitized input (e.g., fields from pysidedeploy.spec)
    # is present.
    executable = shutil.which(str(command[0]))
    if executable:
        command = [executable] + [str(c) for c in command[1:]]

    try:
        if not dry_run:
            if fetch_output:
                output = subprocess.check_output(command)
            else:
                subprocess.check_call(command)
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


@cache
def run_qmlimportscanner(project_dir: Path, dry_run: bool):
    """
        Runs pyside6-qmlimportscanner to find all the imported qml modules in project_dir
    """
    qml_modules = []
    cmd = ["pyside6-qmlimportscanner", "-rootPath", str(project_dir)]

    for ignore_dir in DEFAULT_IGNORE_DIRS:
        cmd.extend(["-exclude", ignore_dir])

    if dry_run:
        run_command(command=cmd, dry_run=True)

    # Run qmlimportscanner during dry_run as well to complete the command being run by nuitka
    _, json_string = run_command(command=cmd, dry_run=False, fetch_output=True)
    json_string = json_string.decode("utf-8")
    json_array = json.loads(json_string)
    qml_modules = [item['name'] for item in json_array if item['type'] == "module"]

    return qml_modules
