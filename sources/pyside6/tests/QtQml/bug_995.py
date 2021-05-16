# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.helper import adjust_filename
from helper.usesqapplication import UsesQApplication

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuick import QQuickView

app = QGuiApplication([])
file = Path(__file__).resolve().parent / 'bug_995.qml'
assert(file.is_file())
view = QQuickView(QUrl.fromLocalFile(file))
view.show()
view.resize(200, 200)
contentItem = view.contentItem()
item = contentItem.childAt(100, 100)

# it CAN NOT crash here
print(item)

