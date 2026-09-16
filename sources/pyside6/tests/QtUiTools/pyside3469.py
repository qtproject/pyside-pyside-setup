# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths  # noqa: E402
init_test_paths(True)

from helper.usesqapplication import UsesQApplication  # noqa: E402

import shiboken6  # noqa: E402
from PySide6.QtUiTools import QUiLoader  # noqa: E402
from PySide6.QtCore import Qt, QTimer, QBuffer  # noqa: E402
from PySide6.QtWidgets import QVBoxLayout, QLabel  # noqa: E402


UI = b"""<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>Form</class>
 <widget class="QWidget" name="Form">
  <layout class="QVBoxLayout" name="outer"/>
 </widget>
</ui>
"""


class QTest(UsesQApplication):
    """PYSIDE-3469: When inserting a python-created inner layout into another
       layout created by C++ on a form created by C++ (typically via QUiLoader),
       and deleting the form via WA_DeleteOnClose, the inner layout's QLayoutItem
       wrappers should be invalidated by the parenting mechanism in libshiboken."""
    def test(self):
        ui = QBuffer()
        ui.setData(UI)
        ui.open(QBuffer.OpenModeFlag.ReadOnly)
        form = QUiLoader().load(ui)  # window and layout created in C++
        ui.close()
        outer = form.outer  # the C++-created layout  (access via object name property)

        inner = QVBoxLayout()  # created from Python, so has a destructor hook
        inner.addWidget(QLabel("My Label"))
        item = inner.itemAt(0)
        outer.addLayout(inner)

        form.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        form.show()
        QTimer.singleShot(0, form.close)  # mimics the user closing the window
        qApp.exec()  # noqa: F821
        self.assertFalse(shiboken6.isValid(form))
        self.assertFalse(shiboken6.isValid(outer))
        self.assertFalse(shiboken6.isValid(item))


if __name__ == '__main__':
    unittest.main()
