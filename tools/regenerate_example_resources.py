# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

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
