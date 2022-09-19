# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from pathlib import Path
import gettext
import sys

from PySide6.QtCore import QItemSelection, Slot
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QListWidget,
                               QMainWindow)


_ = None
ngettext = None


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        file_menu = self.menuBar().addMenu(_("&File"))
        quit_action = file_menu.addAction(_("Quit"))
        quit_action.setShortcut(_("CTRL+Q"))
        quit_action.triggered.connect(self.close)

        self._list_widget = QListWidget()
        self._list_widget.setSelectionMode(QAbstractItemView.MultiSelection)
        self._list_widget.selectionModel().selectionChanged.connect(self.selection_changed)
        self._list_widget.addItem("C++")
        self._list_widget.addItem("Java")
        self._list_widget.addItem("Python")
        self.setCentralWidget(self._list_widget)

    @Slot(QItemSelection, QItemSelection)
    def selection_changed(self, selected, deselected):
        count = len(self._list_widget.selectionModel().selectedRows())
        message = ngettext("{0} language selected",
                           "{0} languages selected", count).format(count)
        self.statusBar().showMessage(message)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    src_dir = Path(__file__).resolve().parent
    try:
        translation = gettext.translation('example', localedir=src_dir / 'locales')
        if translation:
            translation.install()
            _ = translation.gettext
            ngettext = translation.ngettext
    except FileNotFoundError:
        pass
    if not _:
        _ = gettext.gettext
        ngettext = gettext.ngettext
        print('No translation found')

    window = Window()
    window.show()
    sys.exit(app.exec())
