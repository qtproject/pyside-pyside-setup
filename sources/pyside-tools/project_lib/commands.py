# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
# Qt-Security score:critical reason:execute-external-code
from __future__ import annotations

import subprocess
import sys

from . import QTPATHS_CMD, ClOptions

_qtpaths_info: dict[str, str] = {}


def run_command(command: list[str], cwd: str = None, ignore_fail: bool = False) -> int:
    """
    Run a command using a subprocess.
    If dry run is enabled, the command will be printed to stdout instead of being executed.

    :param command: The command to run including the arguments
    :param cwd: The working directory to run the command in
    :param ignore_fail: If True, the current process will not exit if the command fails

    :return: The exit code of the command
    """
    cloptions = ClOptions()
    if not cloptions.quiet or cloptions.dry_run:
        print(" ".join(command))
    if cloptions.dry_run:
        return 0

    ex = subprocess.call(command, cwd=cwd)
    if ex != 0 and not ignore_fail:
        sys.exit(ex)
    return ex


def qtpaths() -> dict[str, str]:
    """Run qtpaths and return a dict of values."""
    global _qtpaths_info
    if not _qtpaths_info:
        output = subprocess.check_output([QTPATHS_CMD, "--query"])
        for line in output.decode("utf-8").split("\n"):
            tokens = line.strip().split(":", maxsplit=1)  # "Path=C:\..."
            if len(tokens) == 2:
                _qtpaths_info[tokens[0]] = tokens[1]
    return _qtpaths_info
