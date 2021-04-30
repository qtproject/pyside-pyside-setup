############################################################################
##
## Copyright (C) 2021 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of the Qt for Python examples of the Qt Toolkit.
##
## $QT_BEGIN_LICENSE:BSD$
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
##
## BSD License Usage
## Alternatively, you may use this file under the terms of the BSD license
## as follows:
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
############################################################################

"""
The gallery example is a simple application with a drawer menu that contains
all the Qt Quick Controls. Each menu item opens a page that shows the
graphical appearance of a control, allows you to interact with the control,
and explains in which circumstances it is handy to use this control.
"""

import os
import sys
import platform

from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtCore import QSettings, QUrl
from PySide6.QtQml import QQmlApplicationEngine, QQmlContext
from PySide6.QtQuickControls2 import QQuickStyle

import rc_gallery

if __name__ == "__main__":
    QGuiApplication.setApplicationName("Gallery")
    QGuiApplication.setOrganizationName("QtProject")

    app = QGuiApplication()
    QIcon.setThemeName("gallery")

    settings = QSettings()
    if not os.environ.get("QT_QUICK_CONTROLS_STYLE"):
        QQuickStyle.setStyle(settings.value("style", str))

    engine = QQmlApplicationEngine()

    built_in_styles = ["Basic", "Fusion", "Imagine", "Material", "Universal"]
    if platform.system() == "Darwin":
        built_in_styles.append("macOS")
    elif platform.system() == "Windows":
        built_in_styles.append("Windows")
    engine.rootContext().setContextProperty("builtInStyles", built_in_styles)

    engine.load(":/gallery.qml")
    rootObjects = engine.rootObjects()
    if not rootObjects:
        sys.exit(-1)

    window = rootObjects[0]
    window.setIcon(QIcon(':/qt-project.org/logos/pysidelogo.png'))

    sys.exit(app.exec())
