# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import sys
from PySide6 import QtCore, QtWidgets

try:
    from PySide6 import QtMacExtras
except ImportError:
    app = QtWidgets.QApplication(sys.argv)
    messageBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical, "QtMacExtras macpasteboardmime",
                                       "This exampe only runs on macOS and QtMacExtras must be installed to run this example.",
                                       QtWidgets.QMessageBox.Close)
    messageBox.exec()
    sys.exit(1)


class VCardMime(QtMacExtras.QMacPasteboardMime):
    def __init__(self, t=QtMacExtras.QMacPasteboardMime.MIME_ALL):
        super().__init__(t)

    def convertorName(self):
        return "VCardMime"

    def canConvert(self, mime, flav):
        if self.mimeFor(flav) == mime:
            return True
        else:
            return False

    def mimeFor(self, flav):
        if flav == "public.vcard":
            return "application/x-mycompany-VCard"
        else:
            return ""

    def flavorFor(self, mime):
        if mime == "application/x-mycompany-VCard":
            return "public.vcard"
        else:
            return ""

    def convertToMime(self, mime, data, flav):
        data_all = QtCore.QByteArray()
        for i in data:
            data_all += i
        return data_all

    def convertFromMime(mime, data, flav):
        # Todo: implement!
        return []


class TestWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vcardMime = VCardMime()
        self.setAcceptDrops(True)

        self.label1 = QtWidgets.QLabel()
        self.label2 = QtWidgets.QLabel()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label1)
        layout.addWidget(self.label2)
        self.setLayout(layout)

        self.label1.setText("Please drag a \"VCard\" from Contacts application, normally a name in the list, and drop here.")

    def dragEnterEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        e.accept()
        self.contentsDropEvent(e)

    def contentsDropEvent(self, e):
        if e.mimeData().hasFormat("application/x-mycompany-VCard"):
            s = e.mimeData().data("application/x-mycompany-VCard")
            # s now contains text of vcard
            self.label2.setText(str(s))
            e.acceptProposedAction()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    QtMacExtras.qRegisterDraggedTypes(["public.vcard"])
    wid1 = TestWidget()
    wid1.show()
    sys.exit(app.exec())
