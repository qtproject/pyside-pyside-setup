# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the bluetooth/heartrate-game example from Qt v6.x"""

from pathlib import Path
import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QCoreApplication, QLoggingCategory

from connectionhandler import ConnectionHandler
from devicefinder import DeviceFinder
from devicehandler import DeviceHandler
from heartrate_global import set_simulator


if __name__ == '__main__':
    parser = ArgumentParser(prog="heartrate-game",
                            formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Generate more output")
    parser.add_argument("-s", "--simulator", action="store_true",
                        help="Use Simulator")
    options = parser.parse_args()
    set_simulator(options.simulator)
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

    engine.addImportPath(Path(__file__).parent)
    engine.loadFromModule("HeartRateGame", "Main")

    if not engine.rootObjects():
        sys.exit(-1)

    ex = QCoreApplication.exec()
    del engine
    sys.exit(ex)
