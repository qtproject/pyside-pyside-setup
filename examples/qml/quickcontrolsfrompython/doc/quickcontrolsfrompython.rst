.. _example_qml_quickcontrolsfrompython:

Qt Quick Controls from Python
=============================

This example shows how to load QtQuick Controls types from Python with
:class:`~PySide6.QtQmlFeatures.load_qml_component` and drive them without any
QML glue code.

``Main.qml`` is a bare ``ApplicationWindow`` with no children. From
Python, a ``Slider``, several ``Label`` instances, and a ``Button`` are
loaded from the ``QtQuick.Controls`` module, parented into the window's
content item, and wired up. A ``QTimer`` animates the slider, a value
label tracks the slider through its ``valueChanged`` signal, and a reset
button resets the slider from Python.

.. literalinclude:: main.py
    :lines: 30-114
