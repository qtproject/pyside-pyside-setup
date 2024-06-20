# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import QLocale, QSignalBlocker, Slot
from PySide6.QtWidgets import QMainWindow
from PySide6.QtTextToSpeech import QTextToSpeech, QVoice

from ui_mainwindow import Ui_MainWindow


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

        self._speech = None
        self._voices = []

        self._ui = Ui_MainWindow()
        self._ui.setupUi(self)

        # Populate engine selection list
        self._ui.engine.addItem("Default", "default")
        engines = QTextToSpeech.availableEngines()
        for engine in engines:
            self._ui.engine.addItem(engine, engine)
        self._ui.engine.setCurrentIndex(0)
        self.engine_selected(0)

        self._ui.pitch.valueChanged.connect(self.set_pitch)
        self._ui.rate.valueChanged.connect(self.set_rate)
        self._ui.volume.valueChanged.connect(self.set_volume)
        self._ui.engine.currentIndexChanged.connect(self.engine_selected)
        self._ui.voice.currentIndexChanged.connect(self.voice_selected)
        self._ui.language.currentIndexChanged.connect(self.language_selected)

    @Slot(int)
    def set_rate(self, rate):
        self._speech.setRate(rate / 10.0)

    @Slot(int)
    def set_pitch(self, pitch):
        self._speech.setPitch(pitch / 10.0)

    @Slot(int)
    def set_volume(self, volume):
        self._speech.setVolume(volume / 100.0)

    @Slot(QTextToSpeech.State)
    def state_changed(self, state):
        if state == QTextToSpeech.Speaking:
            self._ui.statusbar.showMessage("Speech started...")
        elif state == QTextToSpeech.Ready:
            self._ui.statusbar.showMessage("Speech stopped...", 2000)
        elif state == QTextToSpeech.Paused:
            self._ui.statusbar.showMessage("Speech paused...")
        else:
            self._ui.statusbar.showMessage("Speech error!")

        self._ui.pauseButton.setEnabled(state == QTextToSpeech.Speaking)
        self._ui.resumeButton.setEnabled(state == QTextToSpeech.Paused)
        can_stop = state == QTextToSpeech.Speaking or state == QTextToSpeech.Paused
        self._ui.stopButton.setEnabled(can_stop)

    @Slot(int)
    def engine_selected(self, index):
        engine_name = self._ui.engine.itemData(index)
        self._speech = None
        self._speech = (QTextToSpeech(self) if engine_name == "default"
                        else QTextToSpeech(engine_name, self))

        # Block signals of the languages combobox while populating
        current = self._speech.locale()
        with QSignalBlocker(self._ui.language):
            self._ui.language.clear()
            # Populate the languages combobox before connecting its signal.
            locales = self._speech.availableLocales()
            for locale in locales:
                lang = QLocale.languageToString(locale.language())
                territory = QLocale.territoryToString(locale.territory())
                self._ui.language.addItem(f"{lang} ({territory})", locale)
                if locale.name() == current.name():
                    current = locale

        self.set_rate(self._ui.rate.value())
        self.set_pitch(self._ui.pitch.value())
        self.set_volume(self._ui.volume.value())

        self._ui.speakButton.clicked.connect(self.speak_text)
        self._ui.stopButton.clicked.connect(self.stop_speaking)
        self._ui.pauseButton.clicked.connect(self.pause_speaking)
        self._ui.resumeButton.clicked.connect(self._speech.resume)

        self._speech.stateChanged.connect(self.state_changed)
        self._speech.localeChanged.connect(self.locale_changed)

        self.locale_changed(current)

    @Slot()
    def speak_text(self):
        self._speech.say(self._ui.plainTextEdit.toPlainText())

    @Slot()
    def stop_speaking(self):
        self._speech.stop()

    @Slot()
    def pause_speaking(self):
        self._speech.pause()

    @Slot(int)
    def language_selected(self, language):
        locale = self._ui.language.itemData(language)
        self._speech.setLocale(locale)

    @Slot(int)
    def voice_selected(self, index):
        self._speech.setVoice(self._voices[index])

    @Slot(QLocale)
    def locale_changed(self, locale):
        self._ui.language.setCurrentIndex(self._ui.language.findData(locale))

        with QSignalBlocker(self._ui.voice):
            self._ui.voice.clear()
            self._voices = self._speech.availableVoices()
            current_voice = self._speech.voice()
            for voice in self._voices:
                name = voice.name()
                gender = QVoice.genderName(voice.gender())
                age = QVoice.ageName(voice.age())
                self._ui.voice.addItem(f"{name} - {gender} - {age}")
                if voice.name() == current_voice.name():
                    self._ui.voice.setCurrentIndex(self._ui.voice.count() - 1)
