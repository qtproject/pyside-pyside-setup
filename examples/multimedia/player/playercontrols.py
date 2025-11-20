# Copyright (C) 2025 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from PySide6.QtMultimedia import QMediaPlayer, QtAudio
from PySide6.QtWidgets import (QComboBox, QHBoxLayout, QSizePolicy, QSlider, QStyle,
                               QToolButton, QWidget)
from PySide6.QtGui import QPalette
from PySide6.QtCore import qFuzzyCompare, Qt, Signal, Slot


class PlayerControls(QWidget):

    play = Signal()
    pause = Signal()
    stop = Signal()
    previous = Signal()
    changeVolume = Signal(float)
    changeMuting = Signal(bool)
    changeRate = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)

        style = self.style()
        self.m_playerState = QMediaPlayer.PlaybackState.StoppedState
        self.m_playerMuted = False

        self.m_playButton = QToolButton(self)
        self.m_playButton.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.m_playButton.setToolTip("Play")
        self.m_playButton.clicked.connect(self.playClicked)

        self.m_pauseButton = QToolButton(self)
        self.m_pauseButton.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        self.m_pauseButton.setToolTip("Pause")
        self.m_pauseButton.clicked.connect(self.pauseClicked)

        self.m_stopButton = QToolButton(self)
        self.m_stopButton.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_MediaStop))
        self.m_stopButton.setToolTip("Stop")
        self.m_stopButton.clicked.connect(self.stop)

        self.m_previousButton = QToolButton(self)
        self.m_previousButton.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_MediaSkipBackward))  # noqa: E501
        self.m_previousButton.setToolTip("Rewind")
        self.m_previousButton.clicked.connect(self.previous)

        self.m_muteButton = QToolButton(self)
        self.m_muteButton.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_MediaVolume))
        self.m_muteButton.setToolTip("Mute")
        self.m_muteButton.clicked.connect(self.muteClicked)

        self.m_volumeSlider = QSlider(Qt.Orientation.Horizontal, self)
        self.m_volumeSlider.setRange(0, 100)
        sp = self.m_volumeSlider.sizePolicy()
        sp.setHorizontalPolicy(QSizePolicy.Policy.MinimumExpanding)
        self.m_volumeSlider.setSizePolicy(sp)
        self.m_volumeSlider.valueChanged.connect(self.onVolumeSliderValueChanged)

        self.m_rateBox = QComboBox(self)
        self.m_rateBox.setToolTip("Rate")
        self.m_rateBox.addItem("0.5x", 0.5)
        self.m_rateBox.addItem("1.0x", 1.0)
        self.m_rateBox.addItem("2.0x", 2.0)
        self.m_rateBox.setCurrentIndex(1)

        self.m_rateBox.activated.connect(self.updateRate)

        self._doSetState(QMediaPlayer.PlaybackState.StoppedState, True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.m_stopButton)
        layout.addWidget(self.m_previousButton)
        layout.addWidget(self.m_pauseButton)
        layout.addWidget(self.m_playButton)
        layout.addWidget(self.m_muteButton)
        layout.addWidget(self.m_volumeSlider)
        layout.addWidget(self.m_rateBox)

    def state(self):
        return self.m_playerState

    @Slot(QMediaPlayer.PlaybackState)
    def setState(self, state):
        self._doSetState(state, False)

    def _doSetState(self, state, force):
        if state != self.m_playerState or force:
            self.m_playerState = state

            baseColor = self.palette().color(QPalette.ColorRole.Base)
            inactiveStyleSheet = f"background-color: {baseColor.name()}"
            defaultStyleSheet = ""

            if state == QMediaPlayer.PlaybackState.StoppedState:
                self.m_stopButton.setStyleSheet(inactiveStyleSheet)
                self.m_playButton.setStyleSheet(defaultStyleSheet)
                self.m_pauseButton.setStyleSheet(defaultStyleSheet)
            elif state == QMediaPlayer.PlaybackState.PlayingState:
                self.m_stopButton.setStyleSheet(defaultStyleSheet)
                self.m_playButton.setStyleSheet(inactiveStyleSheet)
                self.m_pauseButton.setStyleSheet(defaultStyleSheet)
            elif state == QMediaPlayer.PlaybackState.PausedState:
                self.m_stopButton.setStyleSheet(defaultStyleSheet)
                self.m_playButton.setStyleSheet(defaultStyleSheet)
                self.m_pauseButton.setStyleSheet(inactiveStyleSheet)

    def volume(self):
        linearVolume = QtAudio.convertVolume(self.m_volumeSlider.value() / 100.0,
                                             QtAudio.VolumeScale.LogarithmicVolumeScale,
                                             QtAudio.VolumeScale.LinearVolumeScale)
        return linearVolume

    @Slot("float")
    def setVolume(self, volume):
        logarithmicVolume = QtAudio.convertVolume(volume, QtAudio.VolumeScale.LinearVolumeScale,
                                                  QtAudio.VolumeScale.LogarithmicVolumeScale)
        self.m_volumeSlider.setValue(round(logarithmicVolume * 100.0))

    def isMuted(self):
        return self.m_playerMuted

    @Slot(bool)
    def setMuted(self, muted):
        if muted != self.m_playerMuted:
            self.m_playerMuted = muted
            sp = (QStyle.StandardPixmap.SP_MediaVolumeMuted
                  if muted else QStyle.StandardPixmap.SP_MediaVolume)
            self.m_muteButton.setIcon(self.style().standardIcon(sp))

    @Slot()
    def playClicked(self):
        self.play.emit()

    @Slot()
    def pauseClicked(self):
        self.pause.emit()

    @Slot()
    def muteClicked(self):
        self.changeMuting.emit(not self.m_playerMuted)

    def playbackRate(self):
        return self.m_rateBox.itemData(self.m_rateBox.currentIndex())

    def setPlaybackRate(self, rate):
        for i in range(0, self.m_rateBox.count()):
            if qFuzzyCompare(rate, self.m_rateBox.itemData(i)):
                self.m_rateBox.setCurrentIndex(i)
                return

        self.m_rateBox.addItem(f"{rate}x", rate)
        self.m_rateBox.setCurrentIndex(self.m_rateBox.count() - 1)

    @Slot()
    def updateRate(self):
        self.changeRate.emit(self.playbackRate())

    @Slot()
    def onVolumeSliderValueChanged(self):
        self.changeVolume.emit(self.volume())
