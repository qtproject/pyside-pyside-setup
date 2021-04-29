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
from helper.usesqapplication import UsesQApplication
from PySide6.QtCore import QTimer, QUrl
from PySide6.QtQml import QQmlPropertyMap
from PySide6.QtQuick import QQuickView


class TestBug(UsesQApplication):
    def testQMLFunctionCall(self):
        ownerData = QQmlPropertyMap()
        ownerData.insert('name', 'John Smith')
        ownerData.insert('phone', '555-5555')
        ownerData.insert('newValue', '')

        view = QQuickView()
        ctxt = view.rootContext()
        ctxt.setContextProperty('owner', ownerData)
        file = Path(__file__).resolve().parent / 'bug_997.qml'
        self.assertTrue(file.is_file())
        view.setSource(QUrl.fromLocalFile(os.fspath(file)))
        self.assertTrue(view.rootObject(), quickview_errorstring(view))
        view.show()
        QTimer.singleShot(1000, self.app.quit)
        self.app.exec_()
        self.assertEqual(ownerData.value('newName'), ownerData.value('name'))


if __name__ == '__main__':
    unittest.main()
