# Copyright (C) 2025 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from functools import cache

from PySide6.QtMultimedia import (QAudioBufferOutput, QAudioDevice, QAudioOutput, QMediaDevices,
                                  QMediaFormat, QMediaMetaData, QMediaPlayer)
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QFileDialog, QGridLayout,
                               QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton,
                               QSizePolicy, QSlider, QVBoxLayout, QWidget)
from PySide6.QtGui import QCursor, QPixmap
from PySide6.QtCore import QDir, QLocale, QStandardPaths, QTime, Qt, Signal, Slot

from audiolevelmeter import AudioLevelMeter
from playercontrols import PlayerControls
from videowidget import VideoWidget


MP4 = 'video/mp4'


@cache
def getSupportedMimeTypes():
    result = []
    for f in QMediaFormat().supportedFileFormats(QMediaFormat.ConversionMode.Decode):
        mime_type = QMediaFormat(f).mimeType()
        result.append(mime_type.name())
    if MP4 not in result:
        result.append(MP4)  # Should always be there when using FFMPEG
    return result


class Player(QWidget):

    fullScreenChanged = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_statusInfo = ""
        self.m_mediaDevices = QMediaDevices()
        self.m_player = QMediaPlayer(self)
        self.m_audioOutput = QAudioOutput(self)
        self.m_player.setAudioOutput(self.m_audioOutput)
        self.m_player.durationChanged.connect(self.durationChanged)
        self.m_player.positionChanged.connect(self.positionChanged)
        self.m_player.metaDataChanged.connect(self.metaDataChanged)
        self.m_player.mediaStatusChanged.connect(self.statusChanged)
        self.m_player.bufferProgressChanged.connect(self.bufferingProgress)
        self.m_player.hasVideoChanged.connect(self.videoAvailableChanged)
        self.m_player.errorChanged.connect(self.displayErrorMessage)
        self.m_player.tracksChanged.connect(self.tracksChanged)

        self.m_videoWidget = VideoWidget(self)
        available_geometry = self.screen().availableGeometry()
        self.m_videoWidget.setMinimumSize(available_geometry.width() / 2,
                                          available_geometry.height() / 3)
        self.m_player.setVideoOutput(self.m_videoWidget)

        # audio level meter
        self.m_audioBufferOutput = QAudioBufferOutput(self)
        self.m_player.setAudioBufferOutput(self.m_audioBufferOutput)
        self.m_audioLevelMeter = AudioLevelMeter(self)
        self.m_audioBufferOutput.audioBufferReceived.connect(self.m_audioLevelMeter.onAudioBufferReceived)  # noqa: E501
        self.m_player.playingChanged.connect(self.m_audioLevelMeter.deactivate)

        # player layout
        layout = QVBoxLayout(self)

        # display
        displayLayout = QHBoxLayout()
        displayLayout.addWidget(self.m_videoWidget, 2)
        displayLayout.addWidget(self.m_audioLevelMeter, 3)
        layout.addLayout(displayLayout)

        # duration slider and label
        hLayout = QHBoxLayout()

        self.m_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.m_slider.setRange(0, self.m_player.duration())
        self.m_slider.sliderMoved.connect(self.seek)
        hLayout.addWidget(self.m_slider)

        self.m_labelDuration = QLabel()
        self.m_labelDuration.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        hLayout.addWidget(self.m_labelDuration)
        layout.addLayout(hLayout)

        # controls
        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)

        openButton = QPushButton("Open", self)
        openButton.clicked.connect(self.open)
        controlLayout.addWidget(openButton)
        controlLayout.addStretch(1)

        controls = PlayerControls()
        controls.setState(self.m_player.playbackState())
        controls.setVolume(self.m_audioOutput.volume())
        controls.setMuted(controls.isMuted())

        controls.play.connect(self.m_player.play)
        controls.pause.connect(self.m_player.pause)
        controls.stop.connect(self.m_player.stop)
        controls.previous.connect(self.previousClicked)
        controls.changeVolume.connect(self.m_audioOutput.setVolume)
        controls.changeMuting.connect(self.m_audioOutput.setMuted)
        controls.changeRate.connect(self.m_player.setPlaybackRate)
        controls.stop.connect(self.m_videoWidget.update)

        self.m_player.playbackStateChanged.connect(controls.setState)
        self.m_audioOutput.volumeChanged.connect(controls.setVolume)
        self.m_audioOutput.mutedChanged.connect(controls.setMuted)

        controlLayout.addWidget(controls)
        controlLayout.addStretch(1)

        self.m_fullScreenButton = QPushButton("FullScreen", self)
        self.m_fullScreenButton.setCheckable(True)
        controlLayout.addWidget(self.m_fullScreenButton)

        self.m_pitchCompensationButton = QPushButton("Pitch compensation", self)
        self.m_pitchCompensationButton.setCheckable(True)
        av = self.m_player.pitchCompensationAvailability()
        toolTip = ""
        if av == QMediaPlayer.PitchCompensationAvailability.AlwaysOn:
            self.m_pitchCompensationButton.setEnabled(False)
            self.m_pitchCompensationButton.setChecked(True)
            toolTip = "Pitch compensation always enabled on self backend"
        elif av == QMediaPlayer.PitchCompensationAvailability.Unavailable:
            self.m_pitchCompensationButton.setEnabled(False)
            self.m_pitchCompensationButton.setChecked(False)
            toolTip = "Pitch compensation unavailable on self backend"
        elif av == QMediaPlayer.PitchCompensationAvailability.Available:
            self.m_pitchCompensationButton.setEnabled(True)
            self.m_pitchCompensationButton.setChecked(self.m_player.pitchCompensation())
        self.m_pitchCompensationButton.setToolTip(toolTip)

        controlLayout.addWidget(self.m_pitchCompensationButton)
        self.m_player.pitchCompensationChanged.connect(self._updatePitchCompensation)
        self.m_pitchCompensationButton.setChecked(self.m_player.pitchCompensation())
        self.m_pitchCompensationButton.toggled.connect(self.m_player.setPitchCompensation)

        self.m_audioOutputCombo = QComboBox(self)
        controlLayout.addWidget(self.m_audioOutputCombo)

        self.updateAudioDevices()

        self.m_audioOutputCombo.activated.connect(self.audioOutputChanged)

        self.m_mediaDevices.audioOutputsChanged.connect(self.updateAudioDevices)

        layout.addLayout(controlLayout)

        # tracks
        tracksLayout = QGridLayout()

        self.m_audioTracks = QComboBox(self)
        self.m_audioTracks.activated.connect(self.selectAudioStream)
        tracksLayout.addWidget(QLabel("Audio Tracks:"), 0, 0)
        tracksLayout.addWidget(self.m_audioTracks, 0, 1)

        self.m_videoTracks = QComboBox(self)
        self.m_videoTracks.activated.connect(self.selectVideoStream)
        tracksLayout.addWidget(QLabel("Video Tracks:"), 1, 0)
        tracksLayout.addWidget(self.m_videoTracks, 1, 1)

        self.m_subtitleTracks = QComboBox(self)
        self.m_subtitleTracks.activated.connect(self.selectSubtitleStream)
        tracksLayout.addWidget(QLabel("Subtitle Tracks:"), 2, 0)
        tracksLayout.addWidget(self.m_subtitleTracks, 2, 1)

        layout.addLayout(tracksLayout)

        # metadata
        metaDataLabel = QLabel("Metadata for file:")
        layout.addWidget(metaDataLabel)

        metaDataLayout = QGridLayout()
        metaDataCount = QMediaMetaData.NumMetaData
        self.m_metaDataLabels = [None] * metaDataCount
        self.m_metaDataFields = [None] * metaDataCount
        key = QMediaMetaData.Key.Title.value
        for i in range(0, round((metaDataCount + 2) / 3)):
            for j in range(0, 6, 2):
                labelText = QMediaMetaData.metaDataKeyToString(QMediaMetaData.Key(key))
                self.m_metaDataLabels[key] = QLabel(labelText)
                if (key == QMediaMetaData.Key.ThumbnailImage
                        or key == QMediaMetaData.Key.CoverArtImage):
                    self.m_metaDataFields[key] = QLabel()
                else:
                    lineEdit = QLineEdit()
                    lineEdit.setReadOnly(True)
                    self.m_metaDataFields[key] = lineEdit

                self.m_metaDataLabels[key].setDisabled(True)
                self.m_metaDataFields[key].setDisabled(True)
                metaDataLayout.addWidget(self.m_metaDataLabels[key], i, j)
                metaDataLayout.addWidget(self.m_metaDataFields[key], i, j + 1)
                key += 1
                if key == QMediaMetaData.NumMetaData:
                    break

        layout.addLayout(metaDataLayout)

        if not self.isPlayerAvailable():
            QMessageBox.warning(self, "Service not available",
                                "The QMediaPlayer object does not have a valid service.\n"
                                "Please check the media service plugins are installed.")

            controls.setEnabled(False)
            openButton.setEnabled(False)
            self.m_fullScreenButton.setEnabled(False)
        self.metaDataChanged()

    def closeEvent(self, event):
        self.m_audioLevelMeter.closeRequest()
        event.accept()

    @Slot()
    def _updatePitchCompensation(self):
        self.m_pitchCompensationButton.setChecked(self.m_player.pitchCompensation())

    def isPlayerAvailable(self):
        return self.m_player.isAvailable()

    @Slot()
    def open(self):
        fileDialog = QFileDialog(self)
        fileDialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        fileDialog.setWindowTitle("Open Files")
        fileDialog.setMimeTypeFilters(getSupportedMimeTypes())
        fileDialog.selectMimeTypeFilter(MP4)
        movieDirs = QStandardPaths.standardLocations(QStandardPaths.StandardLocation.MoviesLocation)
        fileDialog.setDirectory(movieDirs[0] if movieDirs else QDir.homePath())
        if fileDialog.exec() == QDialog.DialogCode.Accepted:
            self.openUrl(fileDialog.selectedUrls()[0])

    def openUrl(self, url):
        self.m_player.setSource(url)

    @Slot("qlonglong")
    def durationChanged(self, duration):
        self.m_duration = duration / 1000
        self.m_slider.setMaximum(duration)

    @Slot("qlonglong")
    def positionChanged(self, progress):
        if not self.m_slider.isSliderDown():
            self.m_slider.setValue(progress)
        self.updateDurationInfo(progress / 1000)

    @Slot()
    def metaDataChanged(self):
        metaData = self.m_player.metaData()
        artist = metaData.value(QMediaMetaData.Key.AlbumArtist)
        title = metaData.value(QMediaMetaData.Key.Title)
        trackInfo = QApplication.applicationName()
        if artist and title:
            trackInfo = f"{artist} - {title}"
        elif artist:
            trackInfo = artist
        elif title:
            trackInfo = title
        self.setTrackInfo(trackInfo)

        for i in range(0, QMediaMetaData.NumMetaData):
            field = self.m_metaDataFields[i]
            if isinstance(field, QLineEdit):
                field.clear()
            elif isinstance(field, QLabel):
                field.clear()
            self.m_metaDataFields[i].setDisabled(True)
            self.m_metaDataLabels[i].setDisabled(True)

        for key in metaData.keys():
            i = key.value
            field = self.m_metaDataFields[i]
            if key == QMediaMetaData.Key.CoverArtImage or key == QMediaMetaData.Key.ThumbnailImage:
                if isinstance(field, QLabel):
                    field.setPixmap(QPixmap.fromImage(metaData.value(key)))
            elif isinstance(field, QLineEdit):
                field.setText(metaData.stringValue(key))

            self.m_metaDataFields[i].setDisabled(False)
            self.m_metaDataLabels[i].setDisabled(False)

        tracks = self.m_player.videoTracks()
        currentVideoTrack = self.m_player.activeVideoTrack()
        if currentVideoTrack >= 0 and currentVideoTrack < len(tracks):
            track = tracks[currentVideoTrack]
            trackKeys = track.keys()
            for key in trackKeys:
                i = key.value
                field = self.m_metaDataFields[i]
                if isinstance(field, QLineEdit):
                    stringValue = track.stringValue(key)
                    field.setText(stringValue)
                self.m_metaDataFields[i].setDisabled(True)
                self.m_metaDataLabels[i].setDisabled(True)

    def trackName(self, metaData, index):
        name = ""
        title = metaData.stringValue(QMediaMetaData.Key.Title)
        lang = metaData.value(QMediaMetaData.Key.Language)
        if not title:
            if lang == QLocale.Language.AnyLanguage:
                name = f"Track {index + 1}"
            else:
                name = QLocale.languageToString(lang)
        else:
            if lang == QLocale.Language.AnyLanguage:
                name = title
            else:
                langName = QLocale.languageToString(lang)
                name = f"{title} - [{langName}]"
        return name

    @Slot()
    def tracksChanged(self):
        self.m_audioTracks.clear()
        self.m_videoTracks.clear()
        self.m_subtitleTracks.clear()

        audioTracks = self.m_player.audioTracks()
        self.m_audioTracks.addItem("No audio", -1)
        for i in range(0, len(audioTracks)):
            self.m_audioTracks.addItem(self.trackName(audioTracks[i], i), i)
        self.m_audioTracks.setCurrentIndex(self.m_player.activeAudioTrack() + 1)

        videoTracks = self.m_player.videoTracks()
        self.m_videoTracks.addItem("No video", -1)
        for i in range(0, len(videoTracks)):
            self.m_videoTracks.addItem(self.trackName(videoTracks[i], i), i)
        self.m_videoTracks.setCurrentIndex(self.m_player.activeVideoTrack() + 1)

        self.m_subtitleTracks.addItem("No subtitles", -1)
        subtitleTracks = self.m_player.subtitleTracks()
        for i in range(0, len(subtitleTracks)):
            self.m_subtitleTracks.addItem(self.trackName(subtitleTracks[i], i), i)
        self.m_subtitleTracks.setCurrentIndex(self.m_player.activeSubtitleTrack() + 1)

    @Slot()
    def previousClicked(self):
        self.m_player.setPosition(0)

    @Slot(int)
    def seek(self, mseconds):
        self.m_player.setPosition(mseconds)

    @Slot(QMediaPlayer.MediaStatus)
    def statusChanged(self, status):
        self.handleCursor(status)
        # handle status message
        if (status == QMediaPlayer.MediaStatus.NoMedia
                or status == QMediaPlayer.MediaStatus.LoadedMedia):
            self.setStatusInfo("")
        elif status == QMediaPlayer.MediaStatus.LoadingMedia:
            self.setStatusInfo("Loading...")
        elif (status == QMediaPlayer.MediaStatus.BufferingMedia
              or status == QMediaPlayer.MediaStatus.BufferedMedia):
            progress = round(self.m_player.bufferProgress() * 100.0)
            self.setStatusInfo(f"Buffering {progress}%")
        elif status == QMediaPlayer.MediaStatus.StalledMedia:
            progress = round(self.m_player.bufferProgress() * 100.0)
            self.setStatusInfo(f"Stalled {progress}%")
        elif status == QMediaPlayer.MediaStatus.EndOfMedia:
            QApplication.alert(self)
        elif status == QMediaPlayer.MediaStatus.InvalidMedia:
            self.displayErrorMessage()

    def handleCursor(self, status):
        if (status == QMediaPlayer.MediaStatus.LoadingMedia
                or status == QMediaPlayer.MediaStatus.BufferingMedia
                or status == QMediaPlayer.MediaStatus.StalledMedia):
            self.setCursor(QCursor(Qt.CursorShape.BusyCursor))
        else:
            self.unsetCursor()

    @Slot("float")
    def bufferingProgress(self, progressV):
        progress = round(progressV * 100.0)
        if self.m_player.mediaStatus() == QMediaPlayer.MediaStatus.StalledMedia:
            self.setStatusInfo(f"Stalled {progress}%")
        else:
            self.setStatusInfo(f"Buffering {progress}%")

    @Slot(bool)
    def videoAvailableChanged(self, available):
        if not available:
            self.m_fullScreenButton.clicked.disconnect(self.m_videoWidget.switchToFullScreen)
            self.m_videoWidget.fullScreenChanged.disconnect(self.m_fullScreenButton.setChecked)
            self.m_videoWidget.setFullScreen(False)
        else:
            self.m_fullScreenButton.clicked.connect(self.m_videoWidget.switchToFullScreen)
            self.m_videoWidget.fullScreenChanged.connect(self.m_fullScreenButton.setChecked)
            if self.m_fullScreenButton.isChecked():
                self.m_videoWidget.setFullScreen(True)

    @Slot()
    def selectAudioStream(self):
        stream = self.m_audioTracks.currentData()
        self.m_player.setActiveAudioTrack(stream)

    @Slot()
    def selectVideoStream(self):
        stream = self.m_videoTracks.currentData()
        self.m_player.setActiveVideoTrack(stream)

    @Slot()
    def selectSubtitleStream(self):
        stream = self.m_subtitleTracks.currentData()
        self.m_player.setActiveSubtitleTrack(stream)

    def setTrackInfo(self, info):
        self.m_trackInfo = info
        title = self.m_trackInfo
        if self.m_statusInfo:
            title += f" | {self.m_statusInfo}"
        self.setWindowTitle(title)

    def setStatusInfo(self, info):
        self.m_statusInfo = info
        title = self.m_trackInfo
        if self.m_statusInfo:
            title += f" | {self.m_statusInfo}"
        self.setWindowTitle(title)

    @Slot()
    def displayErrorMessage(self):
        if self.m_player.error() != QMediaPlayer.Error.NoError:
            self.setStatusInfo(self.m_player.errorString())

    def updateDurationInfo(self, currentInfo):
        tStr = ""
        if currentInfo or self.m_duration:
            currentTime = QTime((currentInfo / 3600) % 60, (currentInfo / 60) % 60,
                                currentInfo % 60, (currentInfo * 1000) % 1000)
            totalTime = QTime((self.m_duration / 3600) % 60, (self.m_duration / 60) % 60,
                              self.m_duration % 60, (self.m_duration * 1000) % 1000)
            format = "hh:mm:ss" if self.m_duration > 3600 else "mm:ss"
            tStr = currentTime.toString(format) + " / " + totalTime.toString(format)
        self.m_labelDuration.setText(tStr)

    @Slot()
    def updateAudioDevices(self):
        self.m_audioOutputCombo.clear()

        self.m_audioOutputCombo.addItem("Default", QAudioDevice())
        for deviceInfo in QMediaDevices.audioOutputs():
            self.m_audioOutputCombo.addItem(deviceInfo.description(), deviceInfo)

    @Slot(int)
    def audioOutputChanged(self, index):
        device = self.m_audioOutputCombo.itemData(index)
        self.m_player.audioOutput().setDevice(device)
