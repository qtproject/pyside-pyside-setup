#!/usr/bin/env python
# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
"""B15-2: is the Python type parsed with the meta-object lock held?

One thread, one subprocess, no timing window - which is why this scenario
needs no repeats. Connecting to a signal name that is not declared anywhere
sends libpyside through addMetaMethod(), and that builds the instance
MetaObjectBuilder, which parses the Python type: attribute lookup on every
class member, warnings, delayed enum resolution.

With MetaObjectParseOutsideLock set, the parse runs with no binding lock
held and SBK_ASSERT_NO_RAW_LOCK() at the top of parsePythonType() is
satisfied. Cleared, the parse goes back under the meta-object lock and the
assertion aborts the process.

    PYSIDE6_OPTION_FT unset       ->  ok
    PYSIDE6_OPTION_FT="~0x2000"   ->  CRASH(SIGABRT)

The abort proves the premise of B15-2 - that this path reaches the
interpreter with a binding raw lock held - and nothing more. It is not the
lock inversion itself; that needs the blocking-__getattribute__ scenario.

Debug build only: checkNoRawLock() is empty under NDEBUG, so a release
build answers "ok" in both columns and says nothing.
"""

import sys

from PySide6.QtCore import QObject, SIGNAL, SLOT


class Sender(QObject):
    """Plain enough that the parse has little to do, and still a Python type,
    which is what makes libpyside parse it at all."""


class Receiver(QObject):
    def receiver(self):
        pass


def main() -> int:
    sender = Sender()
    receiver = Receiver()
    # "dynamic()" is declared nowhere. Connecting to it is what makes
    # libpyside build the instance meta object for sender, and building it
    # parses type(sender).
    if not QObject.connect(sender, SIGNAL("dynamic()"), receiver, SLOT("receiver()")):
        print("connect failed - the dynamic signal was not registered")
        return 1
    index = sender.metaObject().indexOfSignal("dynamic()")
    if index < 0:
        print("the signal is not in the instance meta object")
        return 1
    print(f"dynamic signal registered at index {index}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
