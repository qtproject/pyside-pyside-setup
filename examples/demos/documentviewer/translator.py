# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import sys
from PySide6.QtCore import QLocale, QTranslator
from PySide6.QtWidgets import QApplication  # noqa: F401


class Translator:
    def __init__(self):
        self._translator = QTranslator()
        self._baseName = ""
        self._trLocale = QLocale()

    def setBaseName(self, baseName):
        self._baseName = baseName

    def setLanguage(self, lang):
        self._trLocale = QLocale(lang)

    def install(self):
        if not self._baseName:
            print("The basename of the translation is not set. Ignoring.", file=sys.stderr)
            return

        if not self._translator.isEmpty():
            qApp.removeTranslator(self._translator)  # noqa: F821

        if (self._translator.load(self._trLocale, self._baseName, "_", ":/i18n/")
                and qApp.installTranslator(self._translator)):  # noqa: F821
            print("Loaded translation", self._translator.filePath(), file=sys.stderr)
        else:
            if self._trLocale.language() != QLocale.Language.English:
                msg = (f"Failed to load translation {self._baseName} for locale "
                       f"{self._trLocale.name()}. Falling back to English translation")
                print(msg, file=sys.stderr)
                self.setLanguage(QLocale.Language.English)
