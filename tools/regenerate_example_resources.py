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

"""
regenerate_example_resources.py
===============================

Regenerates the QRC resource files of the PySide examples.
"""


import subprocess
import sys
from pathlib import Path


RCC_COMMAND = "pyside6-rcc"
LRELEASE_COMMAND = "lrelease"


def prepare_linguist_example(path):
    """Create the .qm files for the Linguist example which are bundled in the QRC file"""
    translations_dir = path / "translations"
    if not translations_dir.is_dir():
        translations_dir.mkdir(parents=True)

    for ts_file in path.glob("*.ts"):
        qm_file = translations_dir / f"{ts_file.stem}.qm"
        print("Regenerating ", ts_file, qm_file)
        ex = subprocess.call([LRELEASE_COMMAND, ts_file, "-qm", qm_file])
        if ex != 0:
            print(f"{LRELEASE_COMMAND} failed for {ts_file}", file=sys.stderr)
            sys.exit(ex)


def generate_rc_file(qrc_file):
    """Regenerate the QRC resource file."""
    dir = qrc_file.parent
    if dir.name == "linguist":
        prepare_linguist_example(dir)

    target_file = dir / f"{qrc_file.stem}_rc.py"
    if not target_file.is_file():  # prefix naming convention
        target_file2 = qrc_file.parent / f"rc_{qrc_file.stem}.py"
        if target_file2.is_file():
            target_file = target_file2
    if not target_file.is_file():
        print(target_file, " does not exist.", file=sys.stderr)
        return

    print("Regenerating ", qrc_file, target_file)
    ex = subprocess.call([RCC_COMMAND, qrc_file, "-o", target_file])
    if ex != 0:
        print(f"{RCC_COMMAND} failed for {qrc_file}", file=sys.stderr)
        sys.exit(ex)


if __name__ == '__main__':
    examples_path = Path(__file__).resolve().parent.parent / "examples"
    for qrc_file in examples_path.glob("**/*.qrc"):
        generate_rc_file(qrc_file)
