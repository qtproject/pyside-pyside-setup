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

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlEngine, QQmlComponent

app = QGuiApplication(sys.argv)

engine = QQmlEngine()
component = QQmlComponent(engine)

# This should segfault if the QDeclarativeComponent has not QQmlEngine
file = Path(__file__).resolve().parent / 'foo.qml'
assert(not file.is_file())
component.loadUrl(QUrl.fromLocalFile(file))

