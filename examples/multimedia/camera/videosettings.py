# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import os
from PySide6.QtMultimedia import (QCameraFormat, QMediaFormat, QMediaRecorder,
                                  QVideoFrameFormat)
from PySide6.QtWidgets import QDialog

is_android = os.environ.get('ANDROID_ARGUMENT')

if is_android:
    from ui_videosettings_mobile import Ui_VideoSettingsUi
else:
    from ui_videosettings import Ui_VideoSettingsUi


def box_value(box):
    idx = box.currentIndex()
    return None if idx == -1 else box.itemData(idx)


def select_combo_box_item(box, value):
    idx = box.findData(value)
    if idx != -1:
        box.setCurrentIndex(idx)


def to_formatted_string(cameraFormat):
    pf = cameraFormat.pixelFormat()
    format_name = QVideoFrameFormat.pixelFormatToString(pf)
    w = cameraFormat.resolution().width()
    h = cameraFormat.resolution().height()
    min_rate = int(cameraFormat.minFrameRate())
    max_rate = int(cameraFormat.maxFrameRate())
    return f"{format_name} {w}x{h} {min_rate}-{max_rate}FPS"


class VideoSettings(QDialog):

    def __init__(self, mediaRecorder, parent=None):
        super().__init__(parent)

        self._media_recorder = mediaRecorder

        self.m_updatingFormats = False

        self._ui = Ui_VideoSettingsUi()
        self._ui.setupUi(self)

        # sample rate:
        audio_device = self._media_recorder.captureSession().audioInput().device()
        self._ui.audioSampleRateBox.setRange(audio_device.minimumSampleRate(),
                                             audio_device.maximumSampleRate())

        # camera format
        self._ui.videoFormatBox.addItem("Default camera format",
                                        QCameraFormat())

        camera = self._media_recorder.captureSession().camera()
        video_formats = camera.cameraDevice().videoFormats()

        for format in video_formats:
            self._ui.videoFormatBox.addItem(to_formatted_string(format), format)

        self._ui.videoFormatBox.currentIndexChanged.connect(self.video_format_changed)
        self.set_fps_range(camera.cameraFormat())

        self._ui.fpsSlider.valueChanged.connect(self._ui.fpsSpinBox.setValue)
        self._ui.fpsSpinBox.valueChanged.connect(self._ui.fpsSlider.setValue)

        self.update_formats_and_codecs()
        self._ui.audioCodecBox.currentIndexChanged.connect(self.update_formats_and_codecs)
        self._ui.videoCodecBox.currentIndexChanged.connect(self.update_formats_and_codecs)
        self._ui.containerFormatBox.currentIndexChanged.connect(self.update_formats_and_codecs)

        self._ui.qualitySlider.setRange(0, QMediaRecorder.VeryHighQuality.value)

        format = self._media_recorder.mediaFormat()
        select_combo_box_item(self._ui.containerFormatBox, format.fileFormat())
        select_combo_box_item(self._ui.audioCodecBox, format.audioCodec())
        select_combo_box_item(self._ui.videoCodecBox, format.videoCodec())

        self._ui.qualitySlider.setValue(self._media_recorder.quality().value)
        self._ui.audioSampleRateBox.setValue(self._media_recorder.audioSampleRate())
        select_combo_box_item(self._ui.videoFormatBox, camera.cameraFormat())

        self._ui.fpsSlider.setValue(self._media_recorder.videoFrameRate())
        self._ui.fpsSpinBox.setValue(self._media_recorder.videoFrameRate())

    def apply_settings(self):
        format = QMediaFormat()
        format.setFileFormat(box_value(self._ui.containerFormatBox))
        format.setAudioCodec(box_value(self._ui.audioCodecBox))
        format.setVideoCodec(box_value(self._ui.videoCodecBox))

        self._media_recorder.setMediaFormat(format)
        q = self._ui.qualitySlider.value()
        self._media_recorder.setQuality(QMediaRecorder.Quality(q))
        self._media_recorder.setAudioSampleRate(self._ui.audioSampleRateBox.value())

        camera_format = box_value(self._ui.videoFormatBox)
        self._media_recorder.setVideoResolution(camera_format.resolution())
        self._media_recorder.setVideoFrameRate(self._ui.fpsSlider.value())

        camera = self._media_recorder.captureSession().camera()
        camera.setCameraFormat(camera_format)

    def update_formats_and_codecs(self):
        if self.m_updatingFormats:
            return
        self.m_updatingFormats = True

        format = QMediaFormat()
        if self._ui.containerFormatBox.count():
            format.setFileFormat(box_value(self._ui.containerFormatBox))
        if self._ui.audioCodecBox.count():
            format.setAudioCodec(box_value(self._ui.audioCodecBox))
        if self._ui.videoCodecBox.count():
            format.setVideoCodec(box_value(self._ui.videoCodecBox))

        current_index = 0
        self._ui.audioCodecBox.clear()
        self._ui.audioCodecBox.addItem("Default audio codec",
                                       QMediaFormat.AudioCodec.Unspecified)
        for codec in format.supportedAudioCodecs(QMediaFormat.Encode):
            if codec == format.audioCodec():
                current_index = self._ui.audioCodecBox.count()
            desc = QMediaFormat.audioCodecDescription(codec)
            self._ui.audioCodecBox.addItem(desc, codec)

        self._ui.audioCodecBox.setCurrentIndex(current_index)

        current_index = 0
        self._ui.videoCodecBox.clear()
        self._ui.videoCodecBox.addItem("Default video codec",
                                       QMediaFormat.VideoCodec.Unspecified)
        for codec in format.supportedVideoCodecs(QMediaFormat.Encode):
            if codec == format.videoCodec():
                current_index = self._ui.videoCodecBox.count()
            desc = QMediaFormat.videoCodecDescription(codec)
            self._ui.videoCodecBox.addItem(desc, codec)

        self._ui.videoCodecBox.setCurrentIndex(current_index)

        current_index = 0
        self._ui.containerFormatBox.clear()
        self._ui.containerFormatBox.addItem("Default file format",
                                            QMediaFormat.UnspecifiedFormat)
        for container in format.supportedFileFormats(QMediaFormat.Encode):
            if container == format.fileFormat():
                current_index = self._ui.containerFormatBox.count()
            desc = QMediaFormat.fileFormatDescription(container)
            self._ui.containerFormatBox.addItem(desc, container)

        self._ui.containerFormatBox.setCurrentIndex(current_index)

        self.m_updatingFormats = False

    def video_format_changed(self):
        camera_format = box_value(self._ui.videoFormatBox)
        self.set_fps_range(camera_format)

    def set_fps_range(self, format):
        min_fr = format.minFrameRate()
        max_fr = format.maxFrameRate()
        self._ui.fpsSlider.setRange(min_fr, max_fr)
        self._ui.fpsSpinBox.setRange(min_fr, max_fr)
