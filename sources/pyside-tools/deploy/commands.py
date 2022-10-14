# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import subprocess
import sys
import logging

"""
All utility functions for deployment
"""


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
