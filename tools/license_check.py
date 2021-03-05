#############################################################################
##
## Copyright (C) 2021 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of the Qt for Python project.
##
## $QT_BEGIN_LICENSE:LGPL$
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
##
## GNU Lesser General Public License Usage
## Alternatively, this file may be used under the terms of the GNU Lesser
## General Public License version 3 as published by the Free Software
## Foundation and appearing in the file LICENSE.LGPL3 included in the
## packaging of this file. Please review the following information to
## ensure the GNU Lesser General Public License version 3 requirements
## will be met: https://www.gnu.org/licenses/lgpl-3.0.html.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU
## General Public License version 2.0 or (at your option) the GNU General
## Public license version 3 or any later version approved by the KDE Free
## Qt Foundation. The licenses are as published by the Free Software
## Foundation and appearing in the file LICENSE.GPL2 and LICENSE.GPL3
## included in the packaging of this file. Please review the following
## information to ensure the GNU General Public License requirements will
## be met: https://www.gnu.org/licenses/gpl-2.0.html and
## https://www.gnu.org/licenses/gpl-3.0.html.
##
## $QT_END_LICENSE$
##
#############################################################################

import os
from pathlib import Path
import subprocess
import sys


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
