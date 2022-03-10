#############################################################################
##
## Copyright (C) 2016 The Qt Company Ltd.
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

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.helper import quickview_errorstring
from helper.usesqguiapplication import UsesQGuiApplication
from PySide6.QtCore import QCoreApplication, QTimer, QUrl, Slot
from PySide6.QtQml import QQmlPropertyMap
from PySide6.QtQuick import QQuickView


class TestBug(UsesQGuiApplication):

    @Slot()
    def check_complete(self):
        if (self._view.rootObject().isComponentComplete()):
            self._timer.stop()
            self._view.close()

    def testQMLFunctionCall(self):
        ownerData = QQmlPropertyMap()
        ownerData.insert('name', 'John Smith')
        ownerData.insert('phone', '555-5555')
        ownerData.insert('newValue', '')

        self._view = QQuickView()
        self._view.setInitialProperties({'owner': ownerData})
        file = Path(__file__).resolve().parent / 'bug_997.qml'
        self.assertTrue(file.is_file())
        self._view.setSource(QUrl.fromLocalFile(file))
        self.assertTrue(self._view.rootObject(), quickview_errorstring(self._view))
        self._view.show()
        while not self._view.isExposed():
            QCoreApplication.processEvents()
        self._timer = QTimer()
        self._timer.timeout.connect(self.check_complete)
        self._timer.start(20)
        self.app.exec()
        self.assertEqual(ownerData.value('newName'), ownerData.value('name'))


if __name__ == '__main__':
    unittest.main()
