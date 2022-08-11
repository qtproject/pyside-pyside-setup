#############################################################################
##
## Copyright (C) 2022 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
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

"""PySide6 port of the bluetooth/heartrate-game example from Qt v6.x"""

import os
from pathlib import Path
import sys
from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter

from PySide6.QtQml import QQmlApplicationEngine, QQmlContext
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QCoreApplication, QLoggingCategory, QUrl

from connectionhandler import ConnectionHandler
from devicefinder import DeviceFinder
from devicehandler import DeviceHandler
from heartrate_global import simulator


if __name__ == '__main__':
    parser = ArgumentParser(prog="heartrate-game",
                            formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Generate more output")
    parser.add_argument("-s", "--simulator", action="store_true",
                        help="Use Simulator")
    options = parser.parse_args()
    simulator = options.simulator
    if options.verbose:
        QLoggingCategory.setFilterRules("qt.bluetooth* = true")

    app = QGuiApplication(sys.argv)

    connectionHandler = ConnectionHandler()
    deviceHandler = DeviceHandler()
    deviceFinder = DeviceFinder(deviceHandler)

    engine = QQmlApplicationEngine()
    engine.setInitialProperties({
        "connectionHandler": connectionHandler,
        "deviceFinder": deviceFinder,
        "deviceHandler": deviceHandler})

    qml_file = os.fspath(Path(__file__).resolve().parent / "qml" / "main.qml")
    engine.load(QUrl.fromLocalFile(qml_file))
    if not engine.rootObjects():
        sys.exit(-1)

    ex = QCoreApplication.exec()
    del engine
    sys.exit(ex)
