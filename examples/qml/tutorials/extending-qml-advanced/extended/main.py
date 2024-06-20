# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the qml/examples/qml/referenceexamples/extended example from Qt v6.x"""

from pathlib import Path
import sys

from PySide6.QtCore import QObject, QUrl, Property
from PySide6.QtWidgets import QApplication, QLineEdit
from PySide6.QtQml import (QQmlComponent, QQmlEngine, QmlForeign, QmlExtended,
                           QmlNamedElement)


# To be used on the @QmlElement decorator
# (QML_IMPORT_MINOR_VERSION is optional)
QML_IMPORT_NAME = "examples.extend"
QML_IMPORT_MAJOR_VERSION = 1


class LineEditExtension(QObject):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._line_edit = parent

    @Property(int)
    def left_margin(self):
        return self._line_edit.textMargins().left()

    @left_margin.setter
    def left_margin(self, m):
        margins = self._line_edit.textMargins()
        margins.setLeft(m)
        self._line_edit.setTextMargins(margins)

    @Property(int)
    def right_margin(self):
        return self._line_edit.textMargins().right()

    @right_margin.setter
    def right_margin(self, m):
        margins = self._line_edit.textMargins()
        margins.setRight(m)
        self._line_edit.setTextMargins(margins)

    @Property(int)
    def top_margin(self):
        return self._line_edit.textMargins().top()

    @top_margin.setter
    def top_margin(self, m):
        margins = self._line_edit.textMargins()
        margins.setTop(m)
        self._line_edit.setTextMargins(margins)

    @Property(int)
    def bottom_margin(self):
        return self._line_edit.textMargins().bottom()

    @bottom_margin.setter
    def bottom_margin(self, m):
        margins = self._line_edit.textMargins()
        margins.setBottom(m)
        self._line_edit.setTextMargins(margins)


@QmlNamedElement("QLineEdit")
@QmlExtended(LineEditExtension)
@QmlForeign(QLineEdit)
class LineEditForeign(QObject):

    def __init__(self, parent=None):
        super().__init__(parent)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    qml_file = Path(__file__).parent / "example.qml"
    url = QUrl.fromLocalFile(qml_file)
    engine = QQmlEngine()
    component = QQmlComponent(engine, url)
    widget = component.create()
    if not widget:
        print(component.errors())
        del engine
        sys.exit(-1)

    widget.show()
    r = app.exec()
    # Deleting the engine before it goes out of scope is required to make sure
    # all child QML instances are destroyed in the correct order.
    del engine
    sys.exit(r)
