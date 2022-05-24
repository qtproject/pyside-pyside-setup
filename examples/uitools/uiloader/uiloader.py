# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

"""QUiLoader example, showing how to dynamically load a Qt Designer form
   from a UI file."""

from argparse import ArgumentParser, RawTextHelpFormatter
import sys

from PySide6.QtCore import Qt, QFile, QIODevice
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtUiTools import QUiLoader


if __name__ == '__main__':
    arg_parser = ArgumentParser(description="QUiLoader example",
                                formatter_class=RawTextHelpFormatter)
    arg_parser.add_argument('file', type=str, help='UI file')
    args = arg_parser.parse_args()
    ui_file_name = args.file

    app = QApplication(sys.argv)
    ui_file = QFile(ui_file_name)
    if not ui_file.open(QIODevice.ReadOnly):
        reason = ui_file.errorString()
        print(f"Cannot open {ui_file_name}: {reason}")
        sys.exit(-1)
    loader = QUiLoader()
    widget = loader.load(ui_file, None)
    ui_file.close()
    if not widget:
        print(loader.errorString())
        sys.exit(-1)
    widget.show()
    sys.exit(app.exec())
