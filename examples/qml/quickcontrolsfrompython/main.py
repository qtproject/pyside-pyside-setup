# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

"""Load and drive QtQuick Controls types from Python via load_qml_component.

A Slider and several Labels are created from Python with
``load_qml_component(engine, module=..., type_name=...)``, parented into the
ApplicationWindow's content item, and then driven by Python:

  - The Slider's value is animated forward by a QTimer.
  - A value Label updates in real time when the Slider changes (signal).
  - A status Label is updated by Python to show what is happening.
  - A Reset button resets the Slider from Python.

There is no QML glue code. Every control is created from Python.
"""

import sys
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQmlFeatures import load_qml_component
# Importing QtQuick registers the QQuickItem type, so the window's
# contentItem (a QQuickItem) converts to Python.
from PySide6.QtQuick import QQuickItem  # noqa: F401


def main():
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    main_qml = Path(__file__).resolve().parent / "Main.qml"
    engine.load(main_qml)
    if not engine.rootObjects():
        return -1

    # The root object is a raw QObject, not a QmlObject wrapper, so its
    # QML properties are read via property().
    window = engine.rootObjects()[0]
    content = window.property("contentItem")  # drawable area
    win_w = window.property("width")           # 420

    # Load QtQuick Controls types from Python. The engine is passed
    # explicitly. Each create() returns a QmlObject wrapper whose QML
    # properties, signals, and methods are plain Python attributes.
    Label = load_qml_component(engine, module="QtQuick.Controls",
                               type_name="Label")
    Slider = load_qml_component(engine, module="QtQuick.Controls",
                                type_name="Slider")
    Button = load_qml_component(engine, module="QtQuick.Controls",
                                type_name="Button")

    heading = Label.create(text="Qt Controls - driven from Python")
    heading.parent = content
    heading.x = 20
    heading.y = 20

    slider = Slider.create()
    slider.parent = content
    slider.x = 20
    slider.y = 70
    slider.width = win_w - 40
    # Slider range 0.0 - 1.0 (the default), step size 0.01.
    slider.stepSize = 0.01

    value_label = Label.create(text="Value: 0.00")
    value_label.parent = content
    value_label.x = 20
    value_label.y = 130

    def on_value_changed():
        value_label.text = f"Value: {slider.value:.2f}"

    slider.valueChanged.connect(on_value_changed)

    reset_btn = Button.create(text="Reset")
    reset_btn.parent = content
    reset_btn.x = 20
    reset_btn.y = 180

    status_label = Label.create(text="Status: animating...")

    def on_reset():
        slider.value = 0.0
        status_label.text = "Status: reset by Python"

    reset_btn.clicked.connect(on_reset)

    status_label.parent = content
    status_label.x = 120
    status_label.y = 184

    step = [0.0]

    def advance():
        step[0] += 0.02
        if step[0] > 1.0:
            step[0] = 0.0
        slider.value = step[0]
        status_label.text = "Status: animating..."
        print(f"Slider value set to {step[0]:.2f} from Python")

    # The local QTimer stays alive across app.exec() below.
    timer = QTimer()
    timer.timeout.connect(advance)
    timer.start(50)

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
