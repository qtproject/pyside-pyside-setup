#!/usr/bin/env python
# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
"""B12-4/B14-4: a method slot delivers to a receiver that is gone.

Run by run.py.
See README.
"""

import gc
import sys

from PySide6.QtCore import QObject, Signal

# Written before the handler touches self, so a delivery shows even when the
# receiver is no longer readable.
delivered = []


class Sender(QObject):
    fired = Signal()


class Receiver:
    """Not a QObject, which would bypass the dynamic slot."""

    def __init__(self):
        self.hits = 0

    def handler(self):
        delivered.append(id(self))
        self.hits += 1


def main() -> int:
    sender = Sender()
    receiver = Receiver()
    sender.fired.connect(receiver.handler)
    sender.fired.connect(receiver.handler)
    print(f"connected twice, receiver at {hex(id(receiver))}")
    sys.stdout.flush()

    del receiver
    gc.collect()
    print("receiver dropped, emitting")
    sys.stdout.flush()

    sender.fired.emit()

    if delivered:
        # Surviving the delivery is the same defect.
        print(f"delivered to the dead receiver at {hex(delivered[0])}")
        return 1
    print("the dead receiver was not called")
    return 0


if __name__ == "__main__":
    sys.exit(main())
