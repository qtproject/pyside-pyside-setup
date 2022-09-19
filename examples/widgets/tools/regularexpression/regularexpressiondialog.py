# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import re
import logging

from PySide6.QtCore import (QMargins, QRegularExpression, QRegularExpressionMatch,
    QRegularExpressionMatchIterator, Qt, Slot,)
from PySide6.QtGui import (QAction, QColor, QContextMenuEvent, QFontDatabase,
    QGuiApplication, QIcon, QPalette,)
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDialog, QFormLayout,
    QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit,
    QSpinBox, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget,)


def rawStringLiteral(pattern: str) -> str:
    pattern = 'r"' + pattern
    pattern = pattern + '"'
    return pattern


def patternToCode(pattern: str) -> str:
    pattern = pattern.replace("\\", "\\\\")
    pattern = pattern.replace('"', '\\"')
    pattern = '"' + pattern
    pattern = pattern + '"'
    return pattern


def codeToPattern(code: str) -> str:

    try:
        _ = code[0]
    except IndexError:
        logging.warning("code is empty")
        return code

    code_characters = [c for c in code]
    index = 0
    code_characters_size = len(code_characters)
    while index < code_characters_size:
        if code_characters[index] == '\\':
            del code_characters[index]
            code_characters_size -= 1
        index +=1
    code = "".join(code_characters)

    if code.startswith('"') and code.endswith('"'):
        code = code[1:-1]  # remove quotes

    return code


def createHorizontalSeparator() -> QFrame:
    result = QFrame()
    result.setFrameStyle(QFrame.HLine | QFrame.Sunken)
    return result


def createVerticalSeparator() -> QFrame:
    result = QFrame()
    result.setFrameStyle(QFrame.VLine | QFrame.Sunken)
    return result


class PatternLineEdit(QLineEdit):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.escapeSelectionAction = QAction("Escape Selection", self)
        self.copyToCodeAction = QAction("Copy to Code", self)
        self.pasteFromCodeAction = QAction("Paste from Code", self)

        self.setClearButtonEnabled(True)
        self.escapeSelectionAction.triggered.connect(self.escapeSelection)
        self.copyToCodeAction.triggered.connect(self.copyToCode)
        self.pasteFromCodeAction.triggered.connect(self.pasteFromCode)

    @Slot()
    def escapeSelection(self):
        selection = self.selectedText()
        selection_start = self.selectionStart()
        escapedSelection = QRegularExpression.escape(selection)
        if escapedSelection != selection:
            t = self.text()
            t = (
                t[: selection_start]
                + escapedSelection
                + t[selection_start + len(selection) :]
            )
            self.setText(t)

    @Slot()
    def copyToCode(self):
        QGuiApplication.clipboard().setText(patternToCode(self.text()))

    @Slot()
    def pasteFromCode(self):
        self.setText(codeToPattern(QGuiApplication.clipboard().text()))

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        menu = self.createStandardContextMenu()
        menu.setAttribute(Qt.WA_DeleteOnClose)
        menu.addSeparator()
        self.escapeSelectionAction.setEnabled(self.hasSelectedText())
        menu.addAction(self.escapeSelectionAction)
        menu.addSeparator()
        menu.addAction(self.copyToCodeAction)
        menu.addAction(self.pasteFromCodeAction)
        menu.popup(event.globalPos())


class DisplayLineEdit(QLineEdit):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.disablePalette: QPalette = self.palette()
        self.disablePalette.setBrush(
            QPalette.Base,
            self.disablePalette.brush(QPalette.Disabled, QPalette.Base),
        )
        self.setPalette(self.disablePalette)

        self.copyAction = QAction(self)
        self.copyAction.setText("Copy to clipboard")
        self.copyAction.setIcon(QIcon(":/images/copy.png"))
        self.copyAction.triggered.connect(
            lambda: QGuiApplication.clipboard().setText(self.text())
        )
        self.addAction(self.copyAction, QLineEdit.TrailingPosition)


class RegularExpressionDialog(QDialog):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setupUi()
        self.setWindowTitle("QRegularExpression Example")
        self.regularExpression = QRegularExpression()
        self.patternLineEdit.textChanged.connect(self.refresh)
        self.subjectTextEdit.textChanged.connect(self.refresh)
        self.caseInsensitiveOptionCheckBox.toggled.connect(self.refresh)
        self.dotMatchesEverythingOptionCheckBox.toggled.connect(self.refresh)
        self.multilineOptionCheckBox.toggled.connect(self.refresh)
        self.extendedPatternSyntaxOptionCheckBox.toggled.connect(self.refresh)
        self.invertedGreedinessOptionCheckBox.toggled.connect(self.refresh)
        self.dontCaptureOptionCheckBox.toggled.connect(self.refresh)
        self.useUnicodePropertiesOptionCheckBox.toggled.connect(self.refresh)
        self.offsetSpinBox.valueChanged.connect(self.refresh)
        self.matchTypeComboBox.currentIndexChanged.connect(self.refresh)
        self.anchoredMatchOptionCheckBox.toggled.connect(self.refresh)
        self.dontCheckSubjectStringMatchOptionCheckBox.toggled.connect(self.refresh)

        self.patternLineEdit.setText("(\\+?\\d+)-(?P<prefix>\\d+)-(?P<number>\\w+)")
        self.subjectTextEdit.setPlainText(
            "My office number is +43-152-0123456, my mobile is 001-41-255512"
            " instead."
        )

        self.refresh()

    def setResultUiEnabled(self, enabled: bool):
        self.matchDetailsTreeWidget.setEnabled(enabled)
        self.namedGroupsTreeWidget.setEnabled(enabled)
        self.replacementTextEdit.setEnabled(enabled)

    def setTextColor(self, widget: QWidget, color: QColor):
        self.palette: QPalette = widget.palette()
        self.palette.setColor(QPalette.Text, color)
        widget.setPalette(self.palette)

    @Slot()
    def refresh(self):
        self.setUpdatesEnabled(False)
        self.pattern = self.patternLineEdit.text()
        self.text = self.subjectTextEdit.toPlainText()

        self.offsetSpinBox.setMaximum(max(0, len(self.text) - 1))

        self.escapedPatternLineEdit.setText(patternToCode(self.pattern))
        self.rawStringLiteralLineEdit.setText(rawStringLiteral(self.pattern))

        self.setTextColor(
            self.patternLineEdit,
            self.subjectTextEdit.palette().color(QPalette.Text),
        )
        self.matchDetailsTreeWidget.clear()
        self.namedGroupsTreeWidget.clear()
        self.regexpStatusLabel.setText("")
        self.replacementTextEdit.clear()

        if not self.pattern:
            self.setResultUiEnabled(False)
            self.setUpdatesEnabled(True)
            return

        self.regularExpression.setPattern(self.pattern)

        if not self.regularExpression.isValid():
            self.setTextColor(self.patternLineEdit, Qt.red)
            pattern_error_offset = self.regularExpression.patternErrorOffset()
            error_string = self.regularExpression.errorString()
            self.regexpStatusLabel.setText(
                "Invalid: syntax error at position"
                f" {pattern_error_offset}"
                f" ({error_string})"
            )
            self.setResultUiEnabled(False)
            self.setUpdatesEnabled(True)
            return

        self.setResultUiEnabled(True)
        matchType: QRegularExpression.MatchType = QRegularExpression.MatchType(
            self.matchTypeComboBox.currentData()
        )
        patternOptions = QRegularExpression.NoPatternOption
        matchOptions = QRegularExpression.NoMatchOption

        if self.anchoredMatchOptionCheckBox.isChecked():
            matchOptions |= QRegularExpression.AnchorAtOffsetMatchOption
        if self.dontCheckSubjectStringMatchOptionCheckBox.isChecked():
            matchOptions |= QRegularExpression.DontCheckSubjectStringMatchOption

        if self.caseInsensitiveOptionCheckBox.isChecked():
            patternOptions |= QRegularExpression.CaseInsensitiveOption
        if self.dotMatchesEverythingOptionCheckBox.isChecked():
            patternOptions |= QRegularExpression.DotMatchesEverythingOption
        if self.multilineOptionCheckBox.isChecked():
            patternOptions |= QRegularExpression.MultilineOption
        if self.extendedPatternSyntaxOptionCheckBox.isChecked():
            patternOptions |= QRegularExpression.ExtendedPatternSyntaxOption
        if self.invertedGreedinessOptionCheckBox.isChecked():
            patternOptions |= QRegularExpression.InvertedGreedinessOption
        if self.dontCaptureOptionCheckBox.isChecked():
            patternOptions |= QRegularExpression.DontCaptureOption
        if self.useUnicodePropertiesOptionCheckBox.isChecked():
            patternOptions |= QRegularExpression.UseUnicodePropertiesOption

        self.regularExpression.setPatternOptions(patternOptions)

        capturingGroupsCount = self.regularExpression.captureCount() + 1

        offset = self.offsetSpinBox.value()
        iterator: QRegularExpressionMatchIterator = self.regularExpression.globalMatch(
            self.text, offset, matchType, matchOptions
        )
        i = 0

        while iterator.hasNext():
            match: QRegularExpressionMatch = iterator.next()
            matchDetailTopItem = QTreeWidgetItem(self.matchDetailsTreeWidget)
            matchDetailTopItem.setText(0, str(i))

            for captureGroupIndex in range(capturingGroupsCount):
                matchDetailItem = QTreeWidgetItem(matchDetailTopItem)
                matchDetailItem.setText(1, str(captureGroupIndex))
                matchDetailItem.setText(2, match.captured(captureGroupIndex))

            i = i + 1

        self.matchDetailsTreeWidget.expandAll()

        self.regexpStatusLabel.setText("Valid")

        namedCaptureGroups = self.regularExpression.namedCaptureGroups()
        for i in range(len(namedCaptureGroups)):
            currentNamedCaptureGroup = namedCaptureGroups[i]
            namedGroupItem = QTreeWidgetItem(self.namedGroupsTreeWidget)
            namedGroupItem.setText(0, str(i))
            namedGroupItem.setText(
                1,
                "<no name>"
                if not currentNamedCaptureGroup
                else currentNamedCaptureGroup,
            )

        self.updateReplacement()
        self.setUpdatesEnabled(True)

    @Slot()
    def updateReplacement(self):
        self.replacementTextEdit.clear()
        replacement = self.replacementLineEdit.text()
        if not self.regularExpression.isValid() or not replacement:
            return

        current_text = self.subjectTextEdit.toPlainText()
        regular_expression_pattern = self.regularExpression.pattern()

        new_text = re.sub(regular_expression_pattern, replacement, current_text)
        self.replacementTextEdit.setPlainText(new_text)

    def setupUi(self):
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.addWidget(self.setupTextUi())
        self.mainLayout.addWidget(createHorizontalSeparator())

        self.horizontalLayout = QHBoxLayout()
        self.mainLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout.addWidget(self.setupOptionsUi())
        self.horizontalLayout.addWidget(createVerticalSeparator())
        self.horizontalLayout.addWidget(self.setupInfoUi())

        self._font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        self.patternLineEdit.setFont(self._font)
        self.rawStringLiteralLineEdit.setFont(self._font)
        self.escapedPatternLineEdit.setFont(self._font)
        self.replacementLineEdit.setFont(self._font)
        self.subjectTextEdit.setFont(self._font)
        self.replacementTextEdit.setFont(self._font)

    def setupOptionsUi(self):
        container = QWidget()

        form_layout = QFormLayout(container)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_layout.setContentsMargins(QMargins())

        form_layout.addRow(QLabel("<h3>Options</h3>"))

        self.caseInsensitiveOptionCheckBox = QCheckBox("Case insensitive (/i)")
        self.dotMatchesEverythingOptionCheckBox = QCheckBox("Dot matches everything (/s)")
        self.multilineOptionCheckBox = QCheckBox("Multiline (/m)")
        self.extendedPatternSyntaxOptionCheckBox = QCheckBox("Extended pattern (/x)")
        self.invertedGreedinessOptionCheckBox = QCheckBox("Inverted greediness")
        self.dontCaptureOptionCheckBox = QCheckBox("Don't capture")
        self.useUnicodePropertiesOptionCheckBox = QCheckBox("Use unicode properties (/u)")

        self.patternOptionsCheckBoxLayout = QGridLayout()
        gridRow = 0

        self.patternOptionsCheckBoxLayout.addWidget(self.caseInsensitiveOptionCheckBox, gridRow, \
        1)
        self.patternOptionsCheckBoxLayout.addWidget(self.dotMatchesEverythingOptionCheckBox, gridRow\
        ,2)
        gridRow = gridRow + 1
        self.patternOptionsCheckBoxLayout.addWidget(self.multilineOptionCheckBox, gridRow, \
        1)
        self.patternOptionsCheckBoxLayout.addWidget(self.extendedPatternSyntaxOptionCheckBox, gridRow \
        , 2)
        gridRow = gridRow + 1
        self.patternOptionsCheckBoxLayout.addWidget(self.invertedGreedinessOptionCheckBox, gridRow,\
        1)
        self.patternOptionsCheckBoxLayout.addWidget(self.dontCaptureOptionCheckBox, gridRow,\
        2)
        gridRow = gridRow + 1
        self.patternOptionsCheckBoxLayout.addWidget(self.useUnicodePropertiesOptionCheckBox, gridRow,\
        1)

        form_layout.addRow("Pattern options:", self.patternOptionsCheckBoxLayout)

        self.offsetSpinBox = QSpinBox()
        form_layout.addRow("Match &offset:", self.offsetSpinBox)

        self.matchTypeComboBox = QComboBox()
        self.matchTypeComboBox.addItem("Normal", QRegularExpression.NormalMatch)
        self.matchTypeComboBox.addItem(
            "Partial prefer complete",
            QRegularExpression.PartialPreferCompleteMatch,
        )
        self.matchTypeComboBox.addItem(
            "Partial prefer first", QRegularExpression.PartialPreferFirstMatch
        )
        self.matchTypeComboBox.addItem("No match", QRegularExpression.NoMatch)
        form_layout.addRow("Match &type:", self.matchTypeComboBox)

        self.dontCheckSubjectStringMatchOptionCheckBox = QCheckBox(
            "Don't check subject string"
        )
        self.anchoredMatchOptionCheckBox = QCheckBox("Anchored match")

        self.matchOptionsCheckBoxLayout = QGridLayout()
        self.matchOptionsCheckBoxLayout.addWidget(
            self.dontCheckSubjectStringMatchOptionCheckBox, 0, 0
        )
        self.matchOptionsCheckBoxLayout.addWidget(
            self.anchoredMatchOptionCheckBox, 0, 1
        )
        form_layout.addRow("Match options:", self.matchOptionsCheckBoxLayout)

        return container

    def setupInfoUi(self):
        container = QWidget()

        form_layout = QFormLayout(container)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_layout.setContentsMargins(QMargins())

        self.matchInfoLabel = QLabel("<h3>Match information</h3>")
        form_layout.addRow(self.matchInfoLabel)

        self.matchDetailsTreeWidget = QTreeWidget()

        self.matchDetailsTreeWidget.setHeaderLabels(
            ["Match index", "Group index", "Captured string"]
        )
        self.matchDetailsTreeWidget.setSizeAdjustPolicy(QTreeWidget.AdjustToContents)
        form_layout.addRow("Match details:", self.matchDetailsTreeWidget)

        form_layout.addRow(createHorizontalSeparator())

        self.regexpInfoLabel = QLabel("<h3>Regular expression information</h3>")
        form_layout.addRow(self.regexpInfoLabel)

        self.regexpStatusLabel = QLabel("Valid")
        self.regexpStatusLabel.setWordWrap(True)
        form_layout.addRow("Pattern status:", self.regexpStatusLabel)

        self.namedGroupsTreeWidget = QTreeWidget()
        self.namedGroupsTreeWidget.setHeaderLabels(["Index", "Named group"])
        self.namedGroupsTreeWidget.setSizeAdjustPolicy(QTreeWidget.AdjustToContents)
        self.namedGroupsTreeWidget.setRootIsDecorated(False)
        form_layout.addRow("Named groups:", self.namedGroupsTreeWidget)

        return container

    def setupTextUi(self):
        container = QWidget()
        form_layout = QFormLayout(container)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_layout.setContentsMargins(QMargins())

        self.regexpAndSubjectLabel = QLabel(
            "<h3>Regular expression and text input</h3>"
        )
        form_layout.addRow(self.regexpAndSubjectLabel)

        self.patternLineEdit = PatternLineEdit()
        self.patternLineEdit.setClearButtonEnabled(True)
        form_layout.addRow("&Pattern:", self.patternLineEdit)

        self.rawStringLiteralLineEdit = DisplayLineEdit()
        form_layout.addRow("&Raw string literal:", self.rawStringLiteralLineEdit)

        self.escapedPatternLineEdit = DisplayLineEdit()
        form_layout.addRow("&Escaped pattern:", self.escapedPatternLineEdit)

        self.subjectTextEdit = QPlainTextEdit()
        form_layout.addRow("&Subject text:", self.subjectTextEdit)

        form_layout.addRow(createHorizontalSeparator())

        self.replaceLabel = QLabel("<h3>Replacement")
        form_layout.addRow(self.replaceLabel)

        self.replacementLineEdit = QLineEdit()
        self.replacementLineEdit.setClearButtonEnabled(True)
        self.replacementLineEdit.textChanged.connect(self.updateReplacement)
        form_layout.addRow("&Replace by:", self.replacementLineEdit)
        self.replacementLineEdit.setToolTip(
            "Use \\1, \\2... as placeholders for the captured groups."
        )

        self.replacementTextEdit = QPlainTextEdit()
        self.replacementTextEdit.setReadOnly(True)
        form_layout.addRow("Result:", self.replacementTextEdit)

        return container
