# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Unit tests for QOpenGLBuffer'''

import ctypes
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqapplication import UsesQApplication
from PySide6.QtGui import QOffscreenSurface, QOpenGLContext, QSurface, QWindow
from PySide6.QtOpenGL import QOpenGLBuffer


def createSurface(surfaceClass):
    if surfaceClass == QSurface.Window:
        window = QWindow()
        window.setSurfaceType(QWindow.OpenGLSurface)
        window.setGeometry(0, 0, 10, 10)
        window.create()
        return window
    elif surfaceClass == QSurface.Offscreen:
        # Create a window and get the format from that.  For example, if an EGL
        # implementation provides 565 and 888 configs for PBUFFER_BIT but only
        # 888 for WINDOW_BIT, we may end up with a pbuffer surface that is
        # incompatible with the context since it could choose the 565 while the
        # window and the context uses a config with 888.
        format = QSurfaceFormat
        if format.redBufferSize() == -1:
            window = QWindow()
            window.setSurfaceType(QWindow.OpenGLSurface)
            window.setGeometry(0, 0, 10, 10)
            window.create()
            format = window.format()
        offscreenSurface = QOffscreenSurface()
        offscreenSurface.setFormat(format)
        offscreenSurface.create()
        return offscreenSurface
    return 0


class QOpenGLBufferTest(UsesQApplication):
    def testBufferCreate(self):
        surface = createSurface(QSurface.Window)
        ctx = QOpenGLContext()
        ctx.create()
        ctx.makeCurrent(surface)

        buf = QOpenGLBuffer()

        self.assertTrue(not buf.isCreated())

        self.assertTrue(buf.create())
        self.assertTrue(buf.isCreated())

        self.assertEqual(buf.type(), QOpenGLBuffer.VertexBuffer)

        buf.bind()
        buf.allocate(128)
        self.assertEqual(buf.size(), 128)

        buf.release()

        buf.destroy()
        self.assertTrue(not buf.isCreated())

        ctx.doneCurrent()


if __name__ == '__main__':
    unittest.main()
