#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations
import sys
import os
import subprocess
from pathlib import Path


def main():
    # The tools listed as entrypoints in setup.py are copied to 'scripts/..'
    cmd = Path("..") / Path(sys.argv[0]).name
    command = [os.fspath(Path(__file__).parent.resolve() / cmd)]
    command.extend(sys.argv[1:])
    sys.exit(subprocess.call(command))


def genpyi():
    # After we changed the shibokensupport module to be totally virtual,
    # it is no longer possible to call the pyi generator from the file system.
    command = [sys.executable, "-c",
               "import shiboken6;"
               "from shibokensupport.signature.lib.pyi_generator import main;"
               "main()"] + sys.argv[1:]
    sys.exit(subprocess.call(command))


if __name__ == "__main__":
    main()
