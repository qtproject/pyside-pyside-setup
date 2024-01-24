# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

import json
import os
import sys
from enum import Enum
from pathlib import Path
from typing import List, Tuple

"""New project generation code."""


Project = List[Tuple[str, str]]  # tuple of (filename, contents).


class ProjectType(Enum):
    WIDGET_FORM = 1
    WIDGET = 2
    QUICK = 3


_WIDGET_MAIN = """if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
"""


_WIDGET_IMPORTS = """import sys
from PySide6.QtWidgets import QApplication, QMainWindow
"""


_WIDGET_CLASS_DEFINITION = """class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
"""


_WIDGET_SETUP_UI_CODE = """        self._ui = Ui_MainWindow()
        self._ui.setupUi(self)
"""


_MAINWINDOW_FORM = """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>MainWindow</class>
 <widget class="QMainWindow" name="MainWindow">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>800</width>
    <height>600</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>MainWindow</string>
  </property>
  <widget class="QWidget" name="centralwidget"/>
  <widget class="QMenuBar" name="menubar">
   <property name="geometry">
    <rect>
     <x>0</x>
     <y>0</y>
     <width>800</width>
     <height>22</height>
    </rect>
   </property>
  </widget>
  <widget class="QStatusBar" name="statusbar"/>
 </widget>
</ui>
"""


_QUICK_FORM = """import QtQuick
import QtQuick.Controls

ApplicationWindow {
    id: window
    width: 1024
    height: 600
    visible: true
}
"""

_QUICK_MAIN = """import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlApplicationEngine


if __name__ == "__main__":
    app = QGuiApplication()
    engine = QQmlApplicationEngine()
    qml_file = Path(__file__).parent / 'main.qml'
    engine.load(QUrl.fromLocalFile(qml_file))
    if not engine.rootObjects():
        sys.exit(-1)
    exit_code = app.exec()
    del engine
    sys.exit(exit_code)
"""


def _write_project(directory: Path, files: Project):
    """Write out the project."""
    file_list = []
    for file, contents in files:
        (directory / file).write_text(contents)
        print(f"Wrote {directory.name}{os.sep}{file}.")
        file_list.append(file)
    pyproject = {"files": file_list}
    pyproject_file = f"{directory}.pyproject"
    (directory / pyproject_file).write_text(json.dumps(pyproject))
    print(f"Wrote {directory.name}{os.sep}{pyproject_file}.")


def _widget_project() -> Project:
    """Create a (form-less) widgets project."""
    main_py = (_WIDGET_IMPORTS + "\n\n" + _WIDGET_CLASS_DEFINITION + "\n\n"
               + _WIDGET_MAIN)
    return [("main.py", main_py)]


def _ui_form_project() -> Project:
    """Create a Qt Designer .ui form based widgets project."""
    main_py = (_WIDGET_IMPORTS
               + "\nfrom ui_mainwindow import Ui_MainWindow\n\n\n"
               + _WIDGET_CLASS_DEFINITION + _WIDGET_SETUP_UI_CODE
               + "\n\n" + _WIDGET_MAIN)
    return [("main.py", main_py),
            ("mainwindow.ui", _MAINWINDOW_FORM)]


def _qml_project() -> Project:
    """Create a QML project."""
    return [("main.py", _QUICK_MAIN),
            ("main.qml", _QUICK_FORM)]


def new_project(directory_s: str,
                project_type: ProjectType = ProjectType.WIDGET_FORM) -> int:
    directory = Path(directory_s)
    if directory.exists():
        print(f"{directory_s} already exists.", file=sys.stderr)
        return -1
    directory.mkdir(parents=True)

    if project_type == ProjectType.WIDGET_FORM:
        project = _ui_form_project()
    elif project_type == ProjectType.QUICK:
        project = _qml_project()
    else:
        project = _widget_project()
    _write_project(directory, project)
    if project_type == ProjectType.WIDGET_FORM:
        print(f'Run "pyside6-project build {directory_s}" to build the project')
    print(f'Run "python {directory.name}{os.sep}main.py" to run the project')
    return 0
