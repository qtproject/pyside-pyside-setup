
#############################################################################
##
## Copyright (C) 2021 The Qt Company Ltd.
## Contact: http://www.qt.io/licensing/
##
## This file is part of the Qt for Python examples of the Qt Toolkit.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of The Qt Company Ltd nor the names of its
##     contributors may be used to endorse or promote products derived
##     from this software without specific prior written permission.
##
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
## $QT_END_LICENSE$
##
#############################################################################

"""PySide6 Multimedia player example"""

import sys
from PySide6.QtCore import QStandardPaths, Qt, Slot
from PySide6.QtGui import QAction, QIcon, QKeySequence, QScreen
from PySide6.QtWidgets import (QApplication, QDialog, QFileDialog,
    QMainWindow, QSlider, QStyle, QToolBar)
from PySide6.QtMultimedia import QMediaFormat, QMediaPlayer, QMediaPlaylist
from PySide6.QtMultimediaWidgets import QVideoWidget


AVI = "video/x-msvideo"  # AVI


MP4 = 'video/mp4'


def get_supported_mime_types():
    result = []
    for f in QMediaFormat().supportedFileFormats(QMediaFormat.Decode):
        mime_type = QMediaFormat(f).mimeType()
        result.append(mime_type.name())
    return result


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self._playlist = QMediaPlaylist()
        self._player = QMediaPlayer()
        self._player.errorOccurred.connect(self._player_error)

        tool_bar = QToolBar()
        self.addToolBar(tool_bar)

        file_menu = self.menuBar().addMenu("&File")
        icon = QIcon.fromTheme("document-open")
        open_action = QAction(icon, "&Open...", self,
                              shortcut=QKeySequence.Open, triggered=self.open)
        file_menu.addAction(open_action)
        icon = QIcon.fromTheme("application-exit")
        exit_action = QAction(icon, "E&xit", self,
                              shortcut="Ctrl+Q", triggered=self.close)
        file_menu.addAction(exit_action)

        play_menu = self.menuBar().addMenu("&Play")
        style = self.style()
        icon = QIcon.fromTheme("media-playback-start.png",
                               style.standardIcon(QStyle.SP_MediaPlay))
        self._play_action = tool_bar.addAction(icon, "Play")
        self._play_action.triggered.connect(self._player.play)
        play_menu.addAction(self._play_action)

        icon = QIcon.fromTheme("media-skip-backward-symbolic.svg",
                               style.standardIcon(QStyle.SP_MediaSkipBackward))
        self._previous_action = tool_bar.addAction(icon, "Previous")
        self._previous_action.triggered.connect(self.previous_clicked)
        play_menu.addAction(self._previous_action)

        icon = QIcon.fromTheme("media-playback-pause.png",
                               style.standardIcon(QStyle.SP_MediaPause))
        self._pause_action = tool_bar.addAction(icon, "Pause")
        self._pause_action.triggered.connect(self._player.pause)
        play_menu.addAction(self._pause_action)

        icon = QIcon.fromTheme("media-skip-forward-symbolic.svg",
                               style.standardIcon(QStyle.SP_MediaSkipForward))
        self._next_action = tool_bar.addAction(icon, "Next")
        self._next_action.triggered.connect(self.next_clicked)
        play_menu.addAction(self._next_action)

        icon = QIcon.fromTheme("media-playback-stop.png",
                               style.standardIcon(QStyle.SP_MediaStop))
        self._stop_action = tool_bar.addAction(icon, "Stop")
        self._stop_action.triggered.connect(self._ensure_stopped)
        play_menu.addAction(self._stop_action)

        self._volume_slider = QSlider()
        self._volume_slider.setOrientation(Qt.Horizontal)
        self._volume_slider.setMinimum(0)
        self._volume_slider.setMaximum(100)
        available_width = self.screen().availableGeometry().width()
        self._volume_slider.setFixedWidth(available_width / 10)
        self._volume_slider.setValue(self._player.volume())
        self._volume_slider.setTickInterval(10)
        self._volume_slider.setTickPosition(QSlider.TicksBelow)
        self._volume_slider.setToolTip("Volume")
        self._volume_slider.valueChanged.connect(self._player.setVolume)
        tool_bar.addWidget(self._volume_slider)

        about_menu = self.menuBar().addMenu("&About")
        about_qt_act = QAction("About &Qt", self, triggered=qApp.aboutQt)
        about_menu.addAction(about_qt_act)

        self._video_widget = QVideoWidget()
        self.setCentralWidget(self._video_widget)
        self._player.playbackStateChanged.connect(self.update_buttons)
        self._player.setVideoOutput(self._video_widget)

        self.update_buttons(self._player.playbackState())
        self._mime_types = []

    def closeEvent(self, event):
        self._ensure_stopped()
        event.accept()

    @Slot()
    def open(self):
        self._ensure_stopped()
        file_dialog = QFileDialog(self)

        is_windows = sys.platform == 'win32'
        if not self._mime_types:
            self._mime_types = get_supported_mime_types()
            if (is_windows and AVI not in self._mime_types):
                self._mime_types.append(AVI)

        file_dialog.setMimeTypeFilters(self._mime_types)

        default_mimetype = AVI if is_windows else MP4
        if default_mimetype in self._mime_types:
            file_dialog.selectMimeTypeFilter(default_mimetype)

        movies_location = QStandardPaths.writableLocation(QStandardPaths.MoviesLocation)
        file_dialog.setDirectory(movies_location)
        if file_dialog.exec() == QDialog.Accepted:
            url = file_dialog.selectedUrls()[0]
            self._playlist.addMedia(url)
            self._player.setSource(url)
            self._player.play()

    @Slot()
    def _ensure_stopped(self):
        if self._player.playbackState() != QMediaPlayer.StoppedState:
            self._player.stop()

    @Slot()
    def previous_clicked(self):
        # Go to previous track if we are within the first 5 seconds of playback
        # Otherwise, seek to the beginning.
        if self._player.position() <= 5000:
            self._playlist.previous()
            self._player.setSource(self._playlist.currentMedia())
        else:
            self._player.setPosition(0)

    @Slot()
    def next_clicked(self):
        self._playlist.next()
        self._player.setSource(self._playlist.currentMedia())

    def update_buttons(self, state):
        media_count = self._playlist.mediaCount()
        self._play_action.setEnabled(media_count > 0
            and state != QMediaPlayer.PlayingState)
        self._pause_action.setEnabled(state == QMediaPlayer.PlayingState)
        self._stop_action.setEnabled(state != QMediaPlayer.StoppedState)
        self._previous_action.setEnabled(self._player.position() > 0)
        self._next_action.setEnabled(media_count > 1)

    def show_status_message(self, message):
        self.statusBar().showMessage(message, 5000)

    @Slot(QMediaPlayer.Error, str)
    def _player_error(self, error, error_string):
        print(error_string, file=sys.stderr)
        self.show_status_message(error_string)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    available_geometry = main_win.screen().availableGeometry()
    main_win.resize(available_geometry.width() / 3,
                    available_geometry.height() / 2)
    main_win.show()
    sys.exit(app.exec())
