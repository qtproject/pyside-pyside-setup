#############################################################################
##
## Copyright (C) 2022 The Qt Company Ltd.
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

"""
regenerate_example_ui.py
========================

Regenerates the ui files of the PySide examples.
"""


import subprocess
import sys
from pathlib import Path


UIC_COMMAND = "pyside6-uic"


def generate_ui_file(ui_file):
    """Regenerate the ui file."""
    target_file = ui_file.parent / f"ui_{ui_file.stem}.py"
    if not target_file.is_file():
        print(target_file, " does not exist.", file=sys.stderr)
        return

    print("Regenerating ", ui_file, target_file)
    ex = subprocess.call([UIC_COMMAND, ui_file, "-o", target_file])
    if ex != 0:
        print(f"{UIC_COMMAND} failed for {ui_file}", file=sys.stderr)
        sys.exit(ex)


if __name__ == '__main__':
    examples_path = Path(__file__).resolve().parent.parent / "examples"
    for ui_file in examples_path.glob("**/*.ui"):
        generate_ui_file(ui_file)
