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

import sys
from PySide6.QtCore import (QCoreApplication, QDir, QFile, QFileInfo, QMimeData,
                            QMimeDatabase, QUrl, Qt, Slot)
from PySide6.QtGui import (QAction, QActionGroup, QGuiApplication, QClipboard,
                           QCloseEvent, QFont, QFontDatabase, QFontInfo, QIcon,
                           QKeySequence, QPixmap, QTextBlockFormat,
                           QTextCharFormat, QTextCursor, QTextDocumentWriter,
                           QTextList, QTextListFormat)
from PySide6.QtWidgets import (QApplication, QMainWindow, QColorDialog, QComboBox,
                               QDialog, QFileDialog, QFontComboBox, QStatusBar,
                               QTextEdit, QToolBar, QMenu, QMenuBar, QMessageBox)
from PySide6.QtPrintSupport import (QAbstractPrintDialog, QPrinter,
                                    QPrintDialog, QPrintPreviewDialog)


ABOUT = """This example demonstrates Qt's
 rich text editing facilities in self.action, providing an example
 document for you to experiment with."""


MIME_TYPES = ["text/html", "text/markdown", "text/plain"]


RSRC_PATH = ":/images/mac" if sys.platform == 'darwin' else ":/images/win"


STYLES = ["Standard", "Bullet List (Disc)", "Bullet List (Circle)",
          "Bullet List (Square)", "Task List (Unchecked)",
          "Task List (Checked)", "Ordered List (Decimal)",
          "Ordered List (Alpha lower)", "Ordered List (Alpha upper)",
          "Ordered List (Roman lower)", "Ordered List (Roman upper)",
          "Heading 1", "Heading 2", "Heading 3", "Heading 4", "Heading 5",
          "Heading 6"]


class TextEdit(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        if sys.platform == 'darwin':
            setUnifiedTitleAndToolBarOnMac(True)
        self.setWindowTitle(QCoreApplication.applicationName())

        self._text_edit = QTextEdit(self)
        self._text_edit.currentCharFormatChanged.connect(self.current_char_format_changed)
        self._text_edit.cursorPositionChanged.connect(self.cursor_position_changed)
        self.setCentralWidget(self._text_edit)

        self.setToolButtonStyle(Qt.ToolButtonFollowStyle)
        self.setup_file_actions()
        self.setup_edit_actions()
        self.setup_text_actions()

        help_menu = self.menuBar().addMenu("Help")
        help_menu.addAction("About", self.about)
        help_menu.addAction("About &Qt", qApp.aboutQt)

        text_font = QFont("Helvetica")
        text_font.setStyleHint(QFont.SansSerif)
        self._text_edit.setFont(text_font)
        self.font_changed(self._text_edit.font())
        self.color_changed(self._text_edit.textColor())
        self.alignment_changed(self._text_edit.alignment())

        document = self._text_edit.document()
        document.modificationChanged.connect(self._action_save.setEnabled)
        document.modificationChanged.connect(self.setWindowModified)
        document.undoAvailable.connect(self._action_undo.setEnabled)
        document.redoAvailable.connect(self._action_redo.setEnabled)
        self.setWindowModified(document.isModified())
        self._action_save.setEnabled(document.isModified())
        self._action_undo.setEnabled(document.isUndoAvailable())
        self._action_redo.setEnabled(document.isRedoAvailable())

        self._action_cut.setEnabled(False)
        self._text_edit.copyAvailable.connect(self._action_cut.setEnabled)
        self._action_copy.setEnabled(False)
        self._text_edit.copyAvailable.connect(self._action_copy.setEnabled)

        QGuiApplication.clipboard().dataChanged.connect(self.clipboard_data_changed)

        self._text_edit.setFocus()
        self.set_current_file_name('')

        # Use dark text on light background on macOS, also in dark mode.
        if sys.platform == 'darwin':
            pal = self._text_edit.palette()
            pal.setColor(QPalette.Base, QColor(Qt.white))
            pal.setColor(QPalette.Text, QColor(Qt.black))
            self._text_edit.setPalette(pal)

    def closeEvent(self, e):
        if self.maybe_save():
            e.accept()
        else:
            e.ignore()

    def setup_file_actions(self):
        tb = self.addToolBar("File self.actions")
        menu = self.menuBar().addMenu("&File")

        icon = QIcon.fromTheme("document-new", QIcon(RSRC_PATH + "/filenew.png"))
        a = menu.addAction(icon, "&New", self.file_new)
        tb.addAction(a)
        a.setPriority(QAction.LowPriority)
        a.setShortcut(QKeySequence.New)

        icon = QIcon.fromTheme("document-open",
                               QIcon(RSRC_PATH + "/fileopen.png"))
        a = menu.addAction(icon, "&Open...", self.file_open)
        a.setShortcut(QKeySequence.Open)
        tb.addAction(a)

        menu.addSeparator()

        icon = QIcon.fromTheme("document-save",
                               QIcon(RSRC_PATH + "/filesave.png"))
        self._action_save = menu.addAction(icon, "&Save", self.file_save)
        self._action_save.setShortcut(QKeySequence.Save)
        self._action_save.setEnabled(False)
        tb.addAction(self._action_save)

        a = menu.addAction("Save &As...", self.file_save_as)
        a.setPriority(QAction.LowPriority)
        menu.addSeparator()

        icon = QIcon.fromTheme("document-print",
                               QIcon(RSRC_PATH + "/fileprint.png"))
        a = menu.addAction(icon, "&Print...", self.file_print)
        a.setPriority(QAction.LowPriority)
        a.setShortcut(QKeySequence.Print)
        tb.addAction(a)

        icon = QIcon.fromTheme("fileprint", QIcon(RSRC_PATH + "/fileprint.png"))
        menu.addAction(icon, "Print Preview...", self.file_print_preview)

        icon = QIcon.fromTheme("exportpdf", QIcon(RSRC_PATH + "/exportpdf.png"))
        a = menu.addAction(icon, "&Export PDF...", self.file_print_pdf)
        a.setPriority(QAction.LowPriority)
        a.setShortcut(Qt.CTRL | Qt.Key_D)
        tb.addAction(a)

        menu.addSeparator()

        a = menu.addAction("&Quit", self.close)
        a.setShortcut(Qt.CTRL | Qt.Key_Q)

    def setup_edit_actions(self):
        tb = self.addToolBar("Edit self.actions")
        menu = self.menuBar().addMenu("&Edit")

        icon = QIcon.fromTheme("edit-undo",
                               QIcon(RSRC_PATH + "/editundo.png"))
        self._action_undo = menu.addAction(icon, "&Undo", self._text_edit.undo)
        self._action_undo.setShortcut(QKeySequence.Undo)
        tb.addAction(self._action_undo)

        icon = QIcon.fromTheme("edit-redo", QIcon(RSRC_PATH + "/editredo.png"))
        self._action_redo = menu.addAction(icon, "&Redo", self._text_edit.redo)
        self._action_redo.setPriority(QAction.LowPriority)
        self._action_redo.setShortcut(QKeySequence.Redo)
        tb.addAction(self._action_redo)
        menu.addSeparator()

        icon = QIcon.fromTheme("edit-cut", QIcon(RSRC_PATH + "/editcut.png"))
        self._action_cut = menu.addAction(icon, "Cu&t", self._text_edit.cut)
        self._action_cut.setPriority(QAction.LowPriority)
        self._action_cut.setShortcut(QKeySequence.Cut)
        tb.addAction(self._action_cut)

        icon = QIcon.fromTheme("edit-copy", QIcon(RSRC_PATH + "/editcopy.png"))
        self._action_copy = menu.addAction(icon, "&Copy", self._text_edit.copy)
        self._action_copy.setPriority(QAction.LowPriority)
        self._action_copy.setShortcut(QKeySequence.Copy)
        tb.addAction(self._action_copy)

        icon = QIcon.fromTheme("edit-paste", QIcon(RSRC_PATH + "/editpaste.png"))
        self._action_paste = menu.addAction(icon, "&Paste", self._text_edit.paste)
        self._action_paste.setPriority(QAction.LowPriority)
        self._action_paste.setShortcut(QKeySequence.Paste)
        tb.addAction(self._action_paste)

        md = QGuiApplication.clipboard().mimeData()
        if md:
            self._action_paste.setEnabled(md.hasText())

    def setup_text_actions(self):
        tb = self.addToolBar("Format self.actions")
        menu = self.menuBar().addMenu("F&ormat")

        icon = QIcon.fromTheme("format-text-bold",
                               QIcon(RSRC_PATH + "/textbold.png"))
        self._action_text_bold = menu.addAction(icon, "&Bold", self.text_bold)
        self._action_text_bold.setShortcut(Qt.CTRL | Qt.Key_B)
        self._action_text_bold.setPriority(QAction.LowPriority)
        bold = QFont()
        bold.setBold(True)
        self._action_text_bold.setFont(bold)
        tb.addAction(self._action_text_bold)
        self._action_text_bold.setCheckable(True)

        icon = QIcon.fromTheme("format-text-italic",
                               QIcon(RSRC_PATH + "/textitalic.png"))
        self._action_text_italic = menu.addAction(icon, "&Italic", self.text_italic)
        self._action_text_italic.setPriority(QAction.LowPriority)
        self._action_text_italic.setShortcut(Qt.CTRL | Qt.Key_I)
        italic = QFont()
        italic.setItalic(True)
        self._action_text_italic.setFont(italic)
        tb.addAction(self._action_text_italic)
        self._action_text_italic.setCheckable(True)

        icon = QIcon.fromTheme("format-text-underline",
                               QIcon(RSRC_PATH + "/textunder.png"))
        self._action_text_underline = menu.addAction(icon, "&Underline",
                                                     self.text_underline)
        self._action_text_underline.setShortcut(Qt.CTRL | Qt.Key_U)
        self._action_text_underline.setPriority(QAction.LowPriority)
        underline = QFont()
        underline.setUnderline(True)
        self._action_text_underline.setFont(underline)
        tb.addAction(self._action_text_underline)
        self._action_text_underline.setCheckable(True)

        menu.addSeparator()

        icon = QIcon.fromTheme("format-justify-left",
                               QIcon(RSRC_PATH + "/textleft.png"))
        self._action_align_left = QAction(icon, "&Left", self)
        self._action_align_left.setShortcut(Qt.CTRL | Qt.Key_L)
        self._action_align_left.setCheckable(True)
        self._action_align_left.setPriority(QAction.LowPriority)
        icon = QIcon.fromTheme("format-justify-center",
                               QIcon(RSRC_PATH + "/textcenter.png"))
        self._action_align_center = QAction(icon, "C&enter", self)
        self._action_align_center.setShortcut(Qt.CTRL | Qt.Key_E)
        self._action_align_center.setCheckable(True)
        self._action_align_center.setPriority(QAction.LowPriority)
        icon = QIcon.fromTheme("format-justify-right",
                               QIcon(RSRC_PATH + "/textright.png"))
        self._action_align_right = QAction(icon, "&Right", self)
        self._action_align_right.setShortcut(Qt.CTRL | Qt.Key_R)
        self._action_align_right.setCheckable(True)
        self._action_align_right.setPriority(QAction.LowPriority)
        icon = QIcon.fromTheme("format-justify-fill",
                               QIcon(RSRC_PATH + "/textjustify.png"))
        self._action_align_justify = QAction(icon, "&Justify", self)
        self._action_align_justify.setShortcut(Qt.CTRL | Qt.Key_J)
        self._action_align_justify.setCheckable(True)
        self._action_align_justify.setPriority(QAction.LowPriority)
        icon = QIcon.fromTheme("format-indent-more",
                               QIcon(RSRC_PATH + "/format-indent-more.png"))
        self._action_indent_more = menu.addAction(icon, "&Indent", self.indent)
        self._action_indent_more.setShortcut(Qt.CTRL | Qt.Key_BracketRight)
        self._action_indent_more.setPriority(QAction.LowPriority)
        icon = QIcon.fromTheme("format-indent-less",
                               QIcon(RSRC_PATH + "/format-indent-less.png"))
        self._action_indent_less = menu.addAction(icon, "&Unindent",
                                                  self.unindent)
        self._action_indent_less.setShortcut(Qt.CTRL | Qt.Key_BracketLeft)
        self._action_indent_less.setPriority(QAction.LowPriority)

        # Make sure the alignLeft is always left of the alignRight
        align_group = QActionGroup(self)
        align_group.triggered.connect(self.text_align)

        if QGuiApplication.isLeftToRight():
            align_group.addAction(self._action_align_left)
            align_group.addAction(self._action_align_center)
            align_group.addAction(self._action_align_right)
        else:
            align_group.addAction(self._action_align_right)
            align_group.addAction(self._action_align_center)
            align_group.addAction(self._action_align_left)
        align_group.addAction(self._action_align_justify)

        tb.addActions(align_group.actions())
        menu.addActions(align_group.actions())
        tb.addAction(self._action_indent_more)
        tb.addAction(self._action_indent_less)
        menu.addAction(self._action_indent_more)
        menu.addAction(self._action_indent_less)

        menu.addSeparator()

        pix = QPixmap(16, 16)
        pix.fill(Qt.black)
        self._action_text_color = menu.addAction(pix, "&Color...", self.text_color)
        tb.addAction(self._action_text_color)

        icon = QIcon(RSRC_PATH + "/textundercolor.png")
        self._action_underline_color = menu.addAction(icon, "Underline color...",
                                                      self.underline_color)
        tb.addAction(self._action_underline_color)

        menu.addSeparator()

        icon = QIcon.fromTheme("status-checkbox-checked",
                               QIcon(RSRC_PATH + "/checkbox-checked.png"))
        self._action_toggle_check_state = menu.addAction(icon, "Chec&ked")
        self._action_toggle_check_state.toggled.connect(self.set_checked)
        self._action_toggle_check_state.setShortcut(Qt.CTRL | Qt.Key_K)
        self._action_toggle_check_state.setCheckable(True)
        self._action_toggle_check_state.setPriority(QAction.LowPriority)
        tb.addAction(self._action_toggle_check_state)

        tb = self.addToolBar("Format self.actions")
        tb.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)
        self.addToolBarBreak(Qt.TopToolBarArea)
        self.addToolBar(tb)

        self._combo_style = QComboBox(tb)
        tb.addWidget(self._combo_style)
        self._combo_style.addItems(STYLES)

        self._combo_style.activated.connect(self.text_style)

        self._combo_font = QFontComboBox(tb)
        tb.addWidget(self._combo_font)
        self._combo_font.textActivated.connect(self.text_family)

        self._combo_size = QComboBox(tb)
        self._combo_size.setObjectName("comboSize")
        tb.addWidget(self._combo_size)
        self._combo_size.setEditable(True)

        standard_sizes = QFontDatabase.standardSizes()
        for size in standard_sizes:
            self._combo_size.addItem(str(size))
        index = standard_sizes.index(QApplication.font().pointSize())
        self._combo_size.setCurrentIndex(index)

        self._combo_size.textActivated.connect(self.text_size)

    def load(self, f):
        if not QFile.exists(f):
            return False
        file = QFile(f)
        if not file.open(QFile.ReadOnly):
            return False

        data = file.readAll()
        db = QMimeDatabase()
        mime_type_name = db.mimeTypeForFileNameAndData(f, data).name()
        text = data.data().decode('utf8')
        if mime_type_name == "text/html":
            file_url = QUrl(f) if f[0] == ':' else QUrl.fromLocalFile(f)
            options = QUrl.FormattingOptions(QUrl.RemoveFilename)
            self._text_edit.document().setBaseUrl(file_url.adjusted(options))
            self._text_edit.setHtml(text)
        elif mime_type_name == "text/markdown":
            self._text_edit.setMarkdown(text)
        else:
            self._text_edit.setPlainText(text)

        self.set_current_file_name(f)
        return True

    def maybe_save(self):
        if not self._text_edit.document().isModified():
            return True

        ret = QMessageBox.warning(self, QCoreApplication.applicationName(),
                                  "The document has been modified.\n"
                                  "Do you want to save your changes?",
                                  QMessageBox.Save | QMessageBox.Discard
                                  | QMessageBox.Cancel)
        if ret == QMessageBox.Save:
            return self.file_save()
        if ret == QMessageBox.Cancel:
            return False
        return True

    def set_current_file_name(self, fileName):
        self._file_name = fileName
        self._text_edit.document().setModified(False)

        shown_name = QFileInfo(fileName).fileName() if fileName else "untitled.txt"
        app_name = QCoreApplication.applicationName()
        self.setWindowTitle(f"{shown_name}[*] - {app_name}")
        self.setWindowModified(False)

    @Slot()
    def file_new(self):
        if self.maybe_save():
            self._text_edit.clear()
            self.set_current_file_name("")

    @Slot()
    def file_open(self):
        file_dialog = QFileDialog(self, "Open File...")
        file_dialog.setAcceptMode(QFileDialog.AcceptOpen)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setMimeTypeFilters(MIME_TYPES)
        if file_dialog.exec() != QDialog.Accepted:
            return
        fn = file_dialog.selectedFiles()[0]
        native_fn = QDir.toNativeSeparators(fn)
        if self.load(fn):
            self.statusBar().showMessage(f'Opened "{native_fn}"')
        else:
            self.statusBar().showMessage(f'Could not open "{native_fn}"')

    @Slot()
    def file_save(self):
        if not self._file_name or self._file_name.startswith(":/"):
            return fileSaveAs()

        writer = QTextDocumentWriter(self._file_name)
        document = self._text_edit.document()
        success = writer.write(document)
        native_fn = QDir.toNativeSeparators(self._file_name)
        if success:
            document.setModified(False)
            self.statusBar().showMessage(f'Wrote "{native_fn}"')
        else:
            self.statusBar().showMessage(f'Could not write to file "{native_fn}"')
        return success

    @Slot()
    def file_save_as(self):
        file_dialog = QFileDialog(self, "Save as...")
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)

        mime_types = MIME_TYPES
        mime_types.insert(1, "application/vnd.oasis.opendocument.text")
        file_dialog.setMimeTypeFilters(mime_types)
        file_dialog.setDefaultSuffix("odt")
        if file_dialog.exec() != QDialog.Accepted:
            return False
        fn = file_dialog.selectedFiles()[0]
        self.set_current_file_name(fn)
        return self.file_save()

    @Slot()
    def file_print(self):
        printer = QPrinter(QPrinter.HighResolution)
        dlg = QPrintDialog(printer, self)
        if self._text_edit.textCursor().hasSelection():
            dlg.setOption(QAbstractPrintDialog.PrintSelection)
        dlg.setWindowTitle("Print Document")
        if dlg.exec() == QDialog.Accepted:
            self._text_edit.print_(printer)

    @Slot()
    def file_print_preview(self):
        printer = QPrinter(QPrinter.HighResolution)
        preview = QPrintPreviewDialog(printer, self)
        preview.paintRequested.connect(self._text_edit.print_)
        preview.exec()

    @Slot()
    def file_print_pdf(self):
        file_dialog = QFileDialog(self, "Export PDF")
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setMimeTypeFilters(["application/pdf"])
        file_dialog.setDefaultSuffix("pdf")
        if file_dialog.exec() != QDialog.Accepted:
            return
        pdf_file_name = file_dialog.selectedFiles()[0]
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(pdf_file_name)
        self._text_edit.document().print_(printer)
        native_fn = QDir.toNativeSeparators(pdf_file_name)
        self.statusBar().showMessage(f'Exported "{native_fn}"')

    @Slot()
    def text_bold(self):
        fmt = QTextCharFormat()
        weight = QFont.Bold if self._action_text_bold.isChecked() else QFont.Normal
        fmt.setFontWeight(weight)
        self.merge_format_on_word_or_selection(fmt)

    @Slot()
    def text_underline(self):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(self._action_text_underline.isChecked())
        self.merge_format_on_word_or_selection(fmt)

    @Slot()
    def text_italic(self):
        fmt = QTextCharFormat()
        fmt.setFontItalic(self._action_text_italic.isChecked())
        self.merge_format_on_word_or_selection(fmt)

    @Slot(str)
    def text_family(self, f):
        fmt = QTextCharFormat()
        fmt.setFontFamilies({f})
        self.merge_format_on_word_or_selection(fmt)

    @Slot(str)
    def text_size(self, p):
        point_size = float(p)
        if point_size > 0:
            fmt = QTextCharFormat()
            fmt.setFontPointSize(point_size)
            self.merge_format_on_word_or_selection(fmt)

    @Slot(int)
    def text_style(self, styleIndex):
        cursor = self._text_edit.textCursor()
        style = QTextListFormat.ListStyleUndefined
        marker = QTextBlockFormat.MarkerType.NoMarker

        if styleIndex == 1:
            style = QTextListFormat.ListDisc
        elif styleIndex == 2:
            style = QTextListFormat.ListCircle
        elif styleIndex == 3:
            style = QTextListFormat.ListSquare
        elif styleIndex == 4:
            if cursor.currentList():
                style = cursor.currentList().format().style()
            else:
                style = QTextListFormat.ListDisc
            marker = QTextBlockFormat.MarkerType.Unchecked
        elif styleIndex == 5:
            if cursor.currentList():
                style = cursor.currentList().format().style()
            else:
                style = QTextListFormat.ListDisc
            marker = QTextBlockFormat.MarkerType.Checked
        elif styleIndex == 6:
            style = QTextListFormat.ListDecimal
        elif styleIndex == 7:
            style = QTextListFormat.ListLowerAlpha
        elif styleIndex == 8:
            style = QTextListFormat.ListUpperAlpha
        elif styleIndex == 9:
            style = QTextListFormat.ListLowerRoman
        elif styleIndex == 10:
            style = QTextListFormat.ListUpperRoman

        cursor.beginEditBlock()

        block_fmt = cursor.blockFormat()

        if style == QTextListFormat.ListStyleUndefined:
            block_fmt.setObjectIndex(-1)
            # H1 to H6, or Standard
            heading_level = styleIndex - 11 + 1 if styleIndex >= 11 else 0
            block_fmt.setHeadingLevel(heading_level)
            cursor.setBlockFormat(block_fmt)

            # H1 to H6: +3 to -2
            size_adjustment = 4 - heading_level if heading_level != 0 else 0
            fmt = QTextCharFormat()
            fmt.setFontWeight(QFont.Bold if heading_level else QFont.Normal)
            fmt.setProperty(QTextFormat.FontSizeAdjustment, size_adjustment)
            cursor.select(QTextCursor.LineUnderCursor)
            cursor.mergeCharFormat(fmt)
            self._text_edit.mergeCurrentCharFormat(fmt)
        else:
            block_fmt.setMarker(marker)
            cursor.setBlockFormat(block_fmt)
            list_fmt = QTextListFormat()
            if cursor.currentList():
                list_fmt = cursor.currentList().format()
            else:
                list_fmt.setIndent(block_fmt.indent() + 1)
                block_fmt.setIndent(0)
                cursor.setBlockFormat(block_fmt)
            list_fmt.setStyle(style)
            cursor.createList(list_fmt)
        cursor.endEditBlock()

    @Slot()
    def text_color(self):
        col = QColorDialog.getColor(self._text_edit.textColor(), self)
        if not col.isValid():
            return
        fmt = QTextCharFormat()
        fmt.setForeground(col)
        self.merge_format_on_word_or_selection(fmt)
        self.color_changed(col)

    @Slot()
    def underline_color(self):
        col = QColorDialog.getColor(Qt.black, self)
        if not col.isValid():
            return
        fmt = QTextCharFormat()
        fmt.setUnderlineColor(col)
        self.merge_format_on_word_or_selection(fmt)
        self.color_changed(col)

    @Slot(QAction)
    def text_align(self, a):
        if a == self._action_align_left:
            self._text_edit.setAlignment(Qt.AlignLeft | Qt.AlignAbsolute)
        elif a == self._action_align_center:
            self._text_edit.setAlignment(Qt.AlignHCenter)
        elif a == self._action_align_right:
            self._text_edit.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)
        elif a == self._action_align_justify:
            self._text_edit.setAlignment(Qt.AlignJustify)

    @Slot(bool)
    def set_checked(self, checked):
        self.text_style(5 if checked else 4)

    @Slot()
    def indent(self):
        self.modify_indentation(1)

    @Slot()
    def unindent(self):
        self.modify_indentation(-1)

    def modify_indentation(self, amount):
        cursor = self._text_edit.textCursor()
        cursor.beginEditBlock()
        if cursor.currentList():
            list_fmt = cursor.currentList().format()
            # See whether the line above is the list we want to move self item
            # into, or whether we need a new list.
            above = QTextCursor(cursor)
            above.movePosition(QTextCursor.Up)
            if (above.currentList()
                and list_fmt.indent() + amount == above.currentList().format().indent()):
                above.currentList().add(cursor.block())
            else:
                list_fmt.setIndent(list_fmt.indent() + amount)
                cursor.createList(list_fmt)
        else:
            block_fmt = cursor.blockFormat()
            block_fmt.setIndent(block_fmt.indent() + amount)
            cursor.setBlockFormat(block_fmt)
        cursor.endEditBlock()

    @Slot(QTextCharFormat)
    def current_char_format_changed(self, format):
        self.font_changed(format.font())
        self.color_changed(format.foreground().color())

    @Slot()
    def cursor_position_changed(self):
        self.alignment_changed(self._text_edit.alignment())
        list = self._text_edit.textCursor().currentList()
        if list:
            style = list.format().style()
            if style == QTextListFormat.ListDisc:
                self._combo_style.setCurrentIndex(1)
            elif style == QTextListFormat.ListCircle:
                self._combo_style.setCurrentIndex(2)
            elif style == QTextListFormat.ListSquare:
                self._combo_style.setCurrentIndex(3)
            elif style == QTextListFormat.ListDecimal:
                self._combo_style.setCurrentIndex(6)
            elif style == QTextListFormat.ListLowerAlpha:
                self._combo_style.setCurrentIndex(7)
            elif style == QTextListFormat.ListUpperAlpha:
                self._combo_style.setCurrentIndex(8)
            elif style == QTextListFormat.ListLowerRoman:
                self._combo_style.setCurrentIndex(9)
            elif style == QTextListFormat.ListUpperRoman:
                self._combo_style.setCurrentIndex(10)
            else:
                self._combo_style.setCurrentIndex(-1)
            marker = self._text_edit.textCursor().block().blockFormat().marker()
            if marker == QTextBlockFormat.MarkerType.NoMarker:
                self._action_toggle_check_state.setChecked(False)
            elif marker == QTextBlockFormat.MarkerType.Unchecked:
                self._combo_style.setCurrentIndex(4)
                self._action_toggle_check_state.setChecked(False)
            elif marker == QTextBlockFormat.MarkerType.Checked:
                self._combo_style.setCurrentIndex(5)
                self._action_toggle_check_state.setChecked(True)
        else:
            heading_level = self._text_edit.textCursor().blockFormat().headingLevel()
            new_level = heading_level + 10 if heading_level != 0 else 0
            self._combo_style.setCurrentIndex(new_level)

    @Slot()
    def clipboard_data_changed(self):
        md = QGuiApplication.clipboard().mimeData()
        self._action_paste.setEnabled(md and md.hasText())

    @Slot()
    def about(self):
        QMessageBox.about(self, "About", ABOUT)

    def merge_format_on_word_or_selection(self, format):
        cursor = self._text_edit.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)
        cursor.mergeCharFormat(format)
        self._text_edit.mergeCurrentCharFormat(format)

    def font_changed(self, f):
        index = self._combo_font.findText(QFontInfo(f).family())
        self._combo_font.setCurrentIndex(index)
        index = self._combo_size.findText(str(f.pointSize()))
        self._combo_size.setCurrentIndex(index)
        self._action_text_bold.setChecked(f.bold())
        self._action_text_italic.setChecked(f.italic())
        self._action_text_underline.setChecked(f.underline())

    def color_changed(self, c):
        pix = QPixmap(16, 16)
        pix.fill(c)
        self._action_text_color.setIcon(pix)

    def alignment_changed(self, a):
        if a & Qt.AlignLeft:
            self._action_align_left.setChecked(True)
        elif a & Qt.AlignHCenter:
            self._action_align_center.setChecked(True)
        elif a & Qt.AlignRight:
            self._action_align_right.setChecked(True)
        elif a & Qt.AlignJustify:
            self._action_align_justify.setChecked(True)
