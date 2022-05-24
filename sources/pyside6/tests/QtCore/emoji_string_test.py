# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

"""
emoji-string-test.py

This is the original code from the bug report
https://bugreports.qt.io/browse/PYSIDE-336

The only changes are the emoji constant creation which avoids unicode in the
source itself, utf8 encoding in line 1 and a short plausibility test to make
it safely fail.
"""

import os
import sys

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
sys.path.append(os.fspath(Path(__file__).resolve().parents[1] / "util"))
from init_paths import init_test_paths
init_test_paths()

from PySide6.QtCore import QObject, Signal


emoji_str = u'\U0001f632' + u' '  # "😲 "


class TestStuff(QObject):
    testsig = Signal(str)

    def a_nop(self, sendMeAnEmoji):
        print(sendMeAnEmoji)
        return

    def __init__(self):
        super().__init__()
        self.testsig.connect(self.a_nop)
        self.testsig.emit(emoji_str)

    def plausi(self):
        # Python 2 may be built with UCS-2 or UCS-4 support.
        # UCS-2 creates 2 surrogate code points. See
        # https://stackoverflow.com/questions/30775689/python-length-of-unicode-string-confusion
        assert len(emoji_str) == 2 if sys.maxunicode > 0xffff else 3


if __name__ == "__main__":
    mything = TestStuff()
    mything.plausi()
