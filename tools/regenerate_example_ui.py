# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

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
