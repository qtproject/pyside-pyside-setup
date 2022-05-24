# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import os
from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QDialog
from PySide6.QtCore import QBuffer, QIODeviceBase, Slot, QSharedMemory, QDataStream, qVersion
from PySide6.QtGui import QImage, QPixmap
from ui_dialog import Ui_Dialog


class Dialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        v = qVersion()
        name = f"QSharedMemoryExample_v{v}"
        self._shared_memory = QSharedMemory(name)

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.loadFromFileButton.clicked.connect(self.load_from_file)
        self.ui.loadFromSharedMemoryButton.clicked.connect(self.load_from_memory)
        self.setWindowTitle("SharedMemory Example")

    def ensure_detached(self):
        if self._shared_memory.isAttached():
            self.detach()

    def closeEvent(self, e):
        self.ensure_detached()
        e.accept()

    @Slot()
    def load_from_file(self):
        self.ensure_detached()

        self.ui.label.setText("Select an image file")
        dir = Path(__file__).resolve().parent
        fileName, _ = QFileDialog.getOpenFileName(self, "Choose Image",
                                                  os.fspath(dir),
                                                  "Images (*.png *.jpg)")
        if not fileName:
            return
        image = QImage()
        if not image.load(fileName):
            self.ui.label.setText("Selected file is not an image, please select another.")
            return
        self.ui.label.setPixmap(QPixmap.fromImage(image))

        # load into shared memory
        buffer = QBuffer()
        buffer.open(QIODeviceBase.WriteOnly)
        out = QDataStream(buffer)
        out << image
        buffer.close()
        size = buffer.size()

        if not self._shared_memory.create(size):
            self.ui.label.setText("Unable to create shared memory segment.")
            return

        self._shared_memory.lock()
        _to = memoryview(self._shared_memory.data())
        _from = buffer.data().data()
        _to[0:size] = _from[0:size]
        self._shared_memory.unlock()

    @Slot()
    def load_from_memory(self):
        if not self._shared_memory.isAttached() and not self._shared_memory.attach():
            self.ui.label.setText("Unable to attach to shared memory segment.\n"
                                  "Load an image first.")
            return

        self._shared_memory.lock()
        mv = memoryview(self._shared_memory.constData())
        buffer = QBuffer()
        buffer.setData(mv.tobytes())
        buffer.open(QBuffer.ReadOnly)
        _in = QDataStream(buffer)
        image = QImage()
        _in >> image
        buffer.close()
        self._shared_memory.unlock()
        self._shared_memory.detach()

        self.ui.label.setPixmap(QPixmap.fromImage(image))

    def detach(self):
        if not self._shared_memory.detach():
            self.ui.label.setText(tr("Unable to detach from shared memory."))
