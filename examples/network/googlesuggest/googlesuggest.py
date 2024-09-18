# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import (QByteArray, QEvent, QObject, QPoint, Qt, QTimer,
                            QXmlStreamReader, Slot)
from PySide6.QtGui import QPalette
from PySide6.QtNetwork import (QNetworkAccessManager, QNetworkReply,
                               QNetworkRequest)
from PySide6.QtWidgets import QFrame, QTreeWidget, QTreeWidgetItem


class GSuggestCompletion(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.editor = parent
        self.popup = QTreeWidget()
        self.popup.setWindowFlags(Qt.Popup)
        self.popup.setFocusPolicy(Qt.NoFocus)
        self.popup.setFocusProxy(parent)
        self.popup.setMouseTracking(True)

        self.popup.setColumnCount(1)
        self.popup.setUniformRowHeights(True)
        self.popup.setRootIsDecorated(False)
        self.popup.setEditTriggers(QTreeWidget.NoEditTriggers)
        self.popup.setSelectionBehavior(QTreeWidget.SelectRows)
        self.popup.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.popup.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.popup.header().hide()

        self.popup.installEventFilter(self)

        self.popup.itemClicked.connect(self.done_completion)

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.auto_suggest)
        self.editor.textEdited.connect(self.timer.start)

        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self.handle_network_data)

    def eventFilter(self, obj: QObject, ev: QEvent):
        if obj is not self.popup:
            return False
        if ev.type() == QEvent.Type.MouseButtonPress:
            self.popup.hide()
            self.editor.setFocus()
            return True

        if ev.type() == QEvent.Type.KeyPress:
            consumed = False
            key = ev.key()
            if key in (Qt.Key.Key_Enter, Qt.Key.Key_Return):
                self.done_completion()
                consumed = True
            elif key == Qt.Key.Key_Escape:
                self.editor.setFocus()
                self.popup.hide()
                consumed = True
            elif key in (
                Qt.Key.Key_Up,
                Qt.Key.Key_Down,
                Qt.Key.Key_Home,
                Qt.Key.Key_End,
                Qt.Key.Key_PageUp,
                Qt.Key.Key_PageDown,
            ):
                pass
            else:
                self.editor.setFocus()
                self.editor.event(ev)
                self.popup.hide()
            return consumed
        return False

    def show_completion(self, choices: list[str]):
        if not choices:
            return
        pal = self.editor.palette()
        color = pal.color(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText)

        self.popup.setUpdatesEnabled(False)
        self.popup.clear()

        for choice in choices:
            item = QTreeWidgetItem(self.popup)
            item.setText(0, choice)
            item.setForeground(0, color)

        self.popup.setCurrentItem(self.popup.topLevelItem(0))
        self.popup.resizeColumnToContents(0)
        self.popup.setUpdatesEnabled(True)

        self.popup.move(self.editor.mapToGlobal(QPoint(0, self.editor.height())))
        self.popup.setFocus()
        self.popup.show()

    @Slot()
    def done_completion(self):
        self.timer.stop()
        self.popup.hide()
        self.editor.setFocus()
        item = self.popup.currentItem()
        if item:
            self.editor.setText(item.text(0))
            self.editor.returnPressed.emit()

    @Slot()
    def auto_suggest(self):
        s = self.editor.text()
        url = f"https://google.com/complete/search?output=toolbar&q={s}"
        self.network_manager.get(QNetworkRequest(url))

    def prevent_suggest(self):
        self.timer.stop()

    @Slot(QNetworkReply)
    def handle_network_data(self, network_reply: QNetworkReply):
        if network_reply.error() == QNetworkReply.NetworkError.NoError:
            choices: list[str] = []

            response: QByteArray = network_reply.readAll()
            xml = QXmlStreamReader(str(response))
            while not xml.atEnd():
                xml.readNext()
                if xml.tokenType() == QXmlStreamReader.TokenType.StartElement:
                    if xml.name() == "suggestion":
                        s = xml.attributes().value("data")
                        choices.append(s)
            self.show_completion(choices)

        network_reply.deleteLater()
