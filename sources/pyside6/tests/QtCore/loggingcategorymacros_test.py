#############################################################################
##
## Copyright (C) 2022 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of the test suite of Qt for Python.
##
## $QT_BEGIN_LICENSE:GPL-EXCEPT$
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU
## General Public License version 3 as published by the Free Software
## Foundation with exceptions as appearing in the file LICENSE.GPL3-EXCEPT
## included in the packaging of this file. Please review the following
## information to ensure the GNU General Public License requirements will
## be met: https://www.gnu.org/licenses/gpl-3.0.html.
##
## $QT_END_LICENSE$
##
#############################################################################

"""Tests for category logging macros qCDebug, qCInfo, qCWarning, qCCritical"""

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import (QLoggingCategory, QtMsgType, qCDebug, qCWarning, qCInfo,
                            qCCritical, qInstallMessageHandler)

param = None

def handler(msgt, ctx, msg):
    global param
    param = ctx.category + ": " + msg.strip()


class TestQLoggingCategory(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.defaultCategory = QLoggingCategory("default")
        self.debugCategory = QLoggingCategory("debug.log", QtMsgType.QtDebugMsg)
        self.infoCategory = QLoggingCategory("info.log", QtMsgType.QtInfoMsg)
        self.warningCategory = QLoggingCategory("warning.log", QtMsgType.QtWarningMsg)
        self.criticalCategory = QLoggingCategory("critical.log", QtMsgType.QtCriticalMsg)
        qInstallMessageHandler(handler)
        self.no_devices = 2

    def test_qCDebug(self):
        qCDebug(self.defaultCategory, "no device")
        self.assertEqual(param, "default: no device")
        qCDebug(self.debugCategory, f"devices: {self.no_devices}")
        self.assertEqual(param, "debug.log: devices: 2")

        # not updated because category is Info which is above Debug
        # nothing will be printed here
        qCDebug(self.infoCategory, f"devices: {self.no_devices}")
        self.assertEqual(param, "debug.log: devices: 2")

    def test_qCInfo(self):
        qCInfo(self.defaultCategory, "no device")
        self.assertEqual(param, "default: no device")
        qCInfo(self.debugCategory, f"devices: {self.no_devices}")
        self.assertEqual(param, "debug.log: devices: 2")
        qCInfo(self.infoCategory, f"devices: {self.no_devices}")
        self.assertEqual(param, "info.log: devices: 2")

        # not updated because category is Warning which is above Info
        # nothing will be printed here
        qCInfo(self.warningCategory, f"devices: {self.no_devices}")
        self.assertEqual(param, "info.log: devices: 2")

    def test_qCWarning(self):
        qCWarning(self.defaultCategory, "no device")
        self.assertEqual(param, "default: no device")
        qCWarning(self.debugCategory, f"devices: {self.no_devices}")
        self.assertEqual(param, "debug.log: devices: 2")
        qCWarning(self.warningCategory, f"devices: {self.no_devices}")
        self.assertEqual(param, "warning.log: devices: 2")

        # not updated because category is Critical which is above Warning
        # nothing will be printed here
        qCWarning(self.criticalCategory, f"devices: {self.no_devices}")
        self.assertEqual(param, "warning.log: devices: 2")


    def test_qCritical(self):
        qCCritical(self.defaultCategory, "no device")
        self.assertEqual(param, "default: no device")
        qCCritical(self.warningCategory, f"devices: {self.no_devices}")
        self.assertEqual(param, "warning.log: devices: 2")
        qCCritical(self.criticalCategory, f"devices: {self.no_devices}")
        self.assertEqual(param, "critical.log: devices: 2")


if __name__ == '__main__':
    unittest.main()
