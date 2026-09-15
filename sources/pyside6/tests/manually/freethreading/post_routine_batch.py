#!/usr/bin/env python
# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
"""B16-2: a post routine registers another one while the runner walks.

Run by run.py.
See README.
"""

import sys

from PySide6.QtCore import QCoreApplication, qAddPostRoutine

order = []


def inner():
    order.append("inner")


def outer():
    order.append("outer")
    qAddPostRoutine(inner)


def main() -> int:
    app = QCoreApplication([])
    qAddPostRoutine(outer)
    # shutdown(), not "del app": the result has to be read before exit.
    app.shutdown()

    if order != ["outer", "inner"]:
        print(f"post routines ran as {order}, expected ['outer', 'inner']")
        return 1
    print("outer registered inner, and inner ran in the next batch")
    return 0


if __name__ == "__main__":
    sys.exit(main())
