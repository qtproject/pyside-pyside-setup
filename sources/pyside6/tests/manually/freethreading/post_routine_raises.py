#!/usr/bin/env python
# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
"""B16-2: a raising post routine must not leave its exception pending.

Run by run.py.
See README.
"""

import sys

from PySide6.QtCore import QCoreApplication, qAddPostRoutine

ran = []


def raises():
    ran.append("raises")
    raise ValueError("deliberate, so that the next callback finds it pending")


def after():
    ran.append("after")


def main() -> int:
    app = QCoreApplication([])
    qAddPostRoutine(raises)
    qAddPostRoutine(after)
    # shutdown(), not "del app": the result has to be read before exit.
    app.shutdown()

    if ran != ["raises", "after"]:
        print(f"post routines ran as {ran}, expected ['raises', 'after']")
        return 1
    print("the raising callback was reported and the batch went on")
    return 0


if __name__ == "__main__":
    sys.exit(main())
