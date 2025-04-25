# Copyright (C) 2025 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths  # noqa: E402
init_test_paths(False)

from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtWidgets import QApplication, QComboBox, QGraphicsScene, QGraphicsView  # noqa: E402

from helper.usesqapplication import UsesQApplication  # noqa: E402


class BugTest(UsesQApplication):
    """PYSIDE-3069: Test that the conversion of an element of a list
       QGraphicsItem* to QGraphicsProxyWidget* (inheriting QObject/QGraphicsItem)
       works correctly without crash.

       For this, we need a QGraphicsProxyWidget for which no wrapper exists,
       created in C++. So, we populate a combo, add it to the scene and show its
       popup, which creates a top level that is automatically wrapped by
       another QGraphicsProxyWidget. This, we print from the list of items().

       See also PYSIDE-86, PYSIDE-1887."""
    def test(self):
        qApp.setEffectEnabled(Qt.UI_AnimateCombo, False)  # noqa: F821
        cb = QComboBox()
        cb.addItem("i1")
        cb.addItem("i2")
        scene = QGraphicsScene()
        scene.addWidget(cb)
        view = QGraphicsView(scene)
        view.show()
        cb.showPopup()
        while not view.windowHandle().isExposed():
            QApplication.processEvents()
        items = scene.items()
        self.assertEqual(len(items), 2)  # Combo and its popup, created in C++
        for i in items:
            print(i)
        view.close()


if __name__ == "__main__":
    unittest.main()
