# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[2]))
from init_paths import init_test_paths
init_test_paths(False)

from pathlib import Path
from PySide6.QtCore import QObject, Slot
from PySide6.QtQml import QQmlEngine, qmlRegisterType
from PySide6.QtQuickTest import QUICK_TEST_MAIN_WITH_SETUP


"""Copy of the equivalent test in qtdeclarative."""


class QmlRegisterTypeCppType(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)


class CustomTestSetup(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

    @Slot(QQmlEngine)
    def qmlEngineAvailable(self, qmlEngine):
        # Test that modules are successfully imported by the TestCaseCollector
        # that parses the QML files (but doesn't run them). For that to happen,
        # qmlEngineAvailable() must be called before TestCaseCollector does its
        # thing.
        qmlRegisterType(QmlRegisterTypeCppType, "QmlRegisterTypeCppModule", 1, 0,
                        "QmlRegisterTypeCppType")
        import_dir = Path(__file__).parent / "imports"
        qmlEngine.addImportPath(os.fspath(import_dir))
        qmlEngine.rootContext().setContextProperty("qmlEngineAvailableCalled", True)


data_dir = Path(__file__).parent / "data"
exitCode = QUICK_TEST_MAIN_WITH_SETUP("qquicktestsetup", CustomTestSetup, sys.argv,
                                      os.fspath(data_dir))
sys.exit(exitCode)
