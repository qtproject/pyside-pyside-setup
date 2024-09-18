# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the Threaded QOpenGLWidget Example from Qt v6.x"""

import sys

from argparse import ArgumentParser, RawTextHelpFormatter

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QShortcut, QSurfaceFormat
from PySide6.QtCore import QCoreApplication, QPoint, qVersion, Qt

try:
    from OpenGL import GL
except ImportError:
    app = QApplication(sys.argv)
    message = "PyOpenGL must be installed to run this example."
    message_box = QMessageBox(QMessageBox.Icon.Critical,
                              "Threaded QOpenGLWidget Example",
                              message, QMessageBox.StandardButton.Close)
    detail = "Run:\npip install PyOpenGL PyOpenGL_accelerate"
    message_box.setDetailedText(detail)
    message_box.exec()
    sys.exit(1)

from glwidget import GLWidget
from mainwindow import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)

    desc = "Qt Threaded QOpenGLWidget Example"
    parser = ArgumentParser(description=desc,
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument("--single", "-s", action="store_true",
                        help="Single thread")
    options = parser.parse_args()

    QCoreApplication.setApplicationName(desc)
    QCoreApplication.setOrganizationName("QtProject")
    QCoreApplication.setApplicationVersion(qVersion())

    format = QSurfaceFormat()
    format.setDepthBufferSize(16)
    QSurfaceFormat.setDefaultFormat(format)

    # Two top-level windows with two QOpenGLWidget children in each. The
    # rendering for the four QOpenGLWidgets happens on four separate threads.

    top_gl_widget = GLWidget()
    pos = top_gl_widget.screen().availableGeometry().topLeft()
    pos += QPoint(200, 200)
    top_gl_widget.setWindowTitle(desc + " top level")
    top_gl_widget.move(pos)
    top_gl_widget.show()

    functions = top_gl_widget.context().functions()
    vendor = functions.glGetString(GL.GL_VENDOR)
    renderer = functions.glGetString(GL.GL_RENDERER)
    gl_info = f"{vendor}/f{renderer}"

    supports_threading = ("nouveau" not in gl_info and "ANGLE" not in gl_info
                          and "llvmpipe" not in gl_info)
    tool_tip = gl_info
    if not supports_threading:
        tool_tip += "\ndoes not support threaded OpenGL."
    top_gl_widget.setToolTip(tool_tip)
    print(tool_tip)

    close_shortcut = QShortcut(Qt.Modifier.CTRL | Qt.Key.Key_Q, top_gl_widget)
    close_shortcut.activated.connect(QApplication.closeAllWindows)
    close_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)

    mw1 = None
    mw2 = None

    if not options.single and supports_threading:
        pos += QPoint(100, 100)
        mw1 = MainWindow()
        mw1.setToolTip(tool_tip)
        mw1.move(pos)
        mw1.setWindowTitle(f"{desc} #1")
        mw1.show()
        pos += QPoint(100, 100)
        mw2 = MainWindow()
        mw2.setToolTip(tool_tip)
        mw2.move(pos)
        mw2.setWindowTitle(f"{desc} #2")
        mw2.show()

    sys.exit(app.exec())
