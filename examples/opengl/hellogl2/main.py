# Copyright (C) 2023 The Qt Company Ltd.
# Copyright (C) 2013 Riverbank Computing Limited.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the opengl/hellogl2 example from Qt v6.x"""

from argparse import ArgumentParser, RawTextHelpFormatter
import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QSurfaceFormat
from PySide6.QtWidgets import (QApplication, QMessageBox)


try:
    from mainwindow import MainWindow
    from glwidget import GLWidget
except ImportError:
    app = QApplication(sys.argv)
    message_box = QMessageBox(QMessageBox.Icon.Critical, "OpenGL hellogl",
                              "PyOpenGL must be installed to run this example.",
                              QMessageBox.StandardButton.Close)
    message_box.setDetailedText("Run:\npip install PyOpenGL PyOpenGL_accelerate")
    message_box.exec()
    sys.exit(1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    parser = ArgumentParser(description="hellogl2",
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument('--multisample', '-m', action='store_true',
                        help='Use Multisampling')
    parser.add_argument('--coreprofile', '-c', action='store_true',
                        help='Use Core Profile')
    parser.add_argument('--transparent', '-t', action='store_true',
                        help='Transparent Windows')
    options = parser.parse_args()

    fmt = QSurfaceFormat()
    fmt.setDepthBufferSize(24)
    if options.multisample:
        fmt.setSamples(4)
    if options.coreprofile:
        fmt.setVersion(3, 2)
        fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
    QSurfaceFormat.setDefaultFormat(fmt)

    GLWidget.set_transparent(options.transparent)

    main_window = MainWindow()
    if options.transparent:
        main_window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        main_window.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)

    main_window.show()

    res = app.exec()
    sys.exit(res)
