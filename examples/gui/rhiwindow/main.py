# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from argparse import ArgumentParser, RawDescriptionHelpFormatter
import sys

from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QGuiApplication, QRhi, QSurfaceFormat

from rhiwindow import HelloWindow
import rc_rhiwindow  # noqa: F401

if __name__ == "__main__":
    app = QGuiApplication(sys.argv)

    # Use platform-specific defaults when no command-line arguments given.
    graphicsApi = QRhi.Implementation.OpenGLES2
    if sys.platform == "win32":
        graphicsApi = QRhi.Implementation.D3D11
    elif sys.platform == "darwin":
        graphicsApi = QRhi.Implementation.Metal

    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter,
                            description="QRhi render example")
    parser.add_argument("--null", "-n", action="store_true", help="Null")
    parser.add_argument("--opengl", "-g", action="store_true", help="OpenGL")
    parser.add_argument("--d3d11", "-d", action="store_true",
                        help="Direct3D 11")
    parser.add_argument("--d3d12", "-D", action="store_true",
                        help="Direct3D 12")
    parser.add_argument("--metal", "-m", action="store_true",
                        help="Metal")
    args = parser.parse_args()
    if args.null:
        graphicsApi = QRhi.Implementation.Null
    elif args.opengl:
        graphicsApi = QRhi.Implementation.OpenGLES2
    elif args.d3d11:
        graphicsApi = QRhi.Implementation.D3D11
    elif args.d3d12:
        graphicsApi = QRhi.Implementation.D3D12
    elif args.metal:
        graphicsApi = QRhi.Implementation.Metal

    # graphicsApi = QRhi.Vulkan?  detect? needs QVulkanInstance

    # For OpenGL, to ensure there is a depth/stencil buffer for the window.
    # With other APIs this is under the application's control
    # (QRhiRenderBuffer etc.) and so no special setup is needed for those.
    fmt = QSurfaceFormat()
    fmt.setDepthBufferSize(24)
    fmt.setStencilBufferSize(8)
    # Special case macOS to allow using OpenGL there.
    # (the default Metal is the recommended approach, though)
    # gl_VertexID is a GLSL 130 feature, and so the default OpenGL 2.1 context
    # we get on macOS is not sufficient.
    if sys.platform == "darwin":
        fmt.setVersion(4, 1)
        fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
    QSurfaceFormat.setDefaultFormat(fmt)

    window = HelloWindow(graphicsApi)

    window.resize(1280, 720)
    title = QCoreApplication.applicationName() + " - " + window.graphicsApiName()
    window.setTitle(title)
    window.show()

    ret = app.exec()

    # RhiWindow::event() will not get invoked when the
    # PlatformSurfaceAboutToBeDestroyed event is sent during the QWindow
    # destruction. That happens only when exiting via app::quit() instead of
    # the more common QWindow::close(). Take care of it: if the QPlatformWindow
    # is still around (there was no close() yet), get rid of the swapchain
    # while it's not too late.
    if window.isVisible():
        window.releaseSwapChain()

    sys.exit(ret)
