# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import math
import sys
from argparse import ArgumentParser, RawTextHelpFormatter

from PySide6.QtSpatialAudio import (QAudioRoom, QAudioEngine, QAudioListener,
                                    QSpatialSound)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
                               QFileDialog, QFormLayout, QHBoxLayout,
                               QLineEdit, QPushButton, QSlider, QWidget)
from PySide6.QtGui import QGuiApplication, QVector3D, QQuaternion
from PySide6.QtCore import (QCoreApplication, QPropertyAnimation,
                            QStandardPaths, QUrl, Qt, qVersion, Slot)


"""PySide6 port of the spatialaudio/audiopanning example from Qt v6.x"""


class AudioWidget(QWidget):

    def __init__(self):
        super().__init__()
        self._file_dialog = None
        self.setMinimumSize(400, 300)
        form = QFormLayout(self)

        file_layout = QHBoxLayout()
        self._file_edit = QLineEdit()
        self._file_edit.setPlaceholderText("Audio File")
        file_layout.addWidget(self._file_edit)
        self._file_dialog_button = QPushButton("Choose...")
        file_layout.addWidget(self._file_dialog_button)
        form.addRow(file_layout)

        self._azimuth = QSlider(Qt.Orientation.Horizontal)
        self._azimuth.setRange(-180, 180)
        form.addRow("Azimuth (-180 - 180 degree):", self._azimuth)

        self._elevation = QSlider(Qt.Orientation.Horizontal)
        self._elevation.setRange(-90, 90)
        form.addRow("Elevation (-90 - 90 degree)", self._elevation)

        self._distance = QSlider(Qt.Orientation.Horizontal)
        self._distance.setRange(0, 1000)
        self._distance.setValue(100)
        form.addRow("Distance (0 - 10 meter):", self._distance)

        self._occlusion = QSlider(Qt.Orientation.Horizontal)
        self._occlusion.setRange(0, 400)
        form.addRow("Occlusion (0 - 4):", self._occlusion)

        self._room_dimension = QSlider(Qt.Orientation.Horizontal)
        self._room_dimension.setRange(0, 10000)
        self._room_dimension.setValue(1000)
        form.addRow("Room dimension (0 - 100 meter):", self._room_dimension)

        self._reverb_gain = QSlider(Qt.Orientation.Horizontal)
        self._reverb_gain.setRange(0, 500)
        self._reverb_gain.setValue(0)
        form.addRow("Reverb gain (0-5):", self._reverb_gain)

        self._reflection_gain = QSlider(Qt.Orientation.Horizontal)
        self._reflection_gain.setRange(0, 500)
        self._reflection_gain.setValue(0)
        form.addRow("Reflection gain (0-5):", self._reflection_gain)

        self._mode = QComboBox()
        self._mode.addItem("Surround", QAudioEngine.Surround)
        self._mode.addItem("Stereo", QAudioEngine.Stereo)
        self._mode.addItem("Headphone", QAudioEngine.Headphone)

        form.addRow("Output mode:", self._mode)

        self._animate_button = QCheckBox("Animate sound position")
        form.addRow(self._animate_button)

        self._file_edit.textChanged.connect(self.file_changed)
        self._file_dialog_button.clicked.connect(self.open_file_dialog)

        self._azimuth.valueChanged.connect(self.update_position)
        self._elevation.valueChanged.connect(self.update_position)
        self._distance.valueChanged.connect(self.update_position)
        self._occlusion.valueChanged.connect(self.new_occlusion)

        self._room_dimension.valueChanged.connect(self.update_room)
        self._reverb_gain.valueChanged.connect(self.update_room)
        self._reflection_gain.valueChanged.connect(self.update_room)

        self._mode.currentIndexChanged.connect(self.mode_changed)

        self._engine = QAudioEngine()
        self._room = QAudioRoom(self._engine)
        self._room.setWallMaterial(QAudioRoom.BackWall, QAudioRoom.BrickBare)
        self._room.setWallMaterial(QAudioRoom.FrontWall, QAudioRoom.BrickBare)
        self._room.setWallMaterial(QAudioRoom.LeftWall, QAudioRoom.BrickBare)
        self._room.setWallMaterial(QAudioRoom.RightWall, QAudioRoom.BrickBare)
        self._room.setWallMaterial(QAudioRoom.Floor, QAudioRoom.Marble)
        self._room.setWallMaterial(QAudioRoom.Ceiling, QAudioRoom.WoodCeiling)
        self.update_room()

        self._listener = QAudioListener(self._engine)
        self._listener.setPosition(QVector3D())
        self._listener.setRotation(QQuaternion())
        self._engine.start()

        self._sound = QSpatialSound(self._engine)
        self.update_position()

        self._animation = QPropertyAnimation(self._azimuth, b"value")
        self._animation.setDuration(10000)
        self._animation.setStartValue(-180)
        self._animation.setEndValue(180)
        self._animation.setLoopCount(-1)
        self._animate_button.toggled.connect(self.animate_changed)

    def set_file(self, file):
        self._file_edit.setText(file)

    def update_position(self):
        az = self._azimuth.value() / 180. * math.pi
        el = self._elevation.value() / 180. * math.pi
        d = self._distance.value()

        x = d * math.sin(az) * math.cos(el)
        y = d * math.sin(el)
        z = -d * math.cos(az) * math.cos(el)
        self._sound.setPosition(QVector3D(x, y, z))

    @Slot()
    def new_occlusion(self):
        self._sound.setOcclusionIntensity(self._occlusion.value() / 100.)

    @Slot()
    def mode_changed(self):
        self._engine.setOutputMode(self._mode.currentData())

    @Slot(str)
    def file_changed(self, file):
        self._sound.setSource(QUrl.fromLocalFile(file))
        self._sound.setSize(5)
        self._sound.setLoops(QSpatialSound.Infinite)

    @Slot()
    def open_file_dialog(self):
        if not self._file_dialog:
            directory = QStandardPaths.writableLocation(QStandardPaths.MusicLocation)
            self._file_dialog = QFileDialog(self, "Open Audio File", directory)
            self._file_dialog.setAcceptMode(QFileDialog.AcceptOpen)
            mime_types = ["audio/mpeg", "audio/aac", "audio/x-ms-wma",
                          "audio/x-flac+ogg", "audio/x-wav"]
            self._file_dialog.setMimeTypeFilters(mime_types)
            self._file_dialog.selectMimeTypeFilter(mime_types[0])

        if self._file_dialog.exec() == QDialog.Accepted:
            self._file_edit.setText(self._file_dialog.selectedFiles()[0])

    @Slot()
    def update_room(self):
        d = self._room_dimension.value()
        self._room.setDimensions(QVector3D(d, d, 400))
        self._room.setReflectionGain(float(self._reflection_gain.value()) / 100)
        self._room.setReverbGain(float(self._reverb_gain.value()) / 100)

    @Slot()
    def animate_changed(self):
        if self._animate_button.isChecked():
            self._animation.start()
        else:
            self._animation.stop()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    name = "Spatial Audio Test Application"
    QCoreApplication.setApplicationVersion(qVersion())
    QGuiApplication.setApplicationDisplayName(name)

    argument_parser = ArgumentParser(description=name,
                                     formatter_class=RawTextHelpFormatter)
    argument_parser.add_argument("file", help="File",
                                 nargs='?', type=str)
    options = argument_parser.parse_args()

    w = AudioWidget()
    w.show()

    if options.file:
        w.set_file(options.file)

    sys.exit(app.exec())
