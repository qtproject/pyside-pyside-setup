# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import os
import subprocess
import sys
from pathlib import Path

"""Tool to run a license check

Requires the qtqa repo to be checked out as sibling.
"""


REPO_DIR = Path(__file__).resolve().parents[1]


if __name__ == '__main__':
    license_check = (REPO_DIR.parent / 'qtqa' / 'tests' / 'prebuild'
                     / 'license' / 'tst_licenses.pl')
    print('Checking ', license_check)
    if not license_check.is_file():
        print('Not found, please clone the qtqa repo')
        sys.exit(1)

    os.environ['QT_MODULE_TO_TEST'] = str(REPO_DIR)
    cmd = [str(license_check), '-m', 'pyside-setup']
    cmds = ' '.join(cmd)
    print('Running: ', cmds)
    ex = subprocess.call(cmd)
    if ex != 0:
        print('FAIL! ', cmds)
        sys.exit(1)
