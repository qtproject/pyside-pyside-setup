.. _example_qml_qmlcomponentloading:

QML Component Loading
=====================

This example shows how to load a QML-defined type from Python with
:class:`~PySide6.QtQmlFeatures.load_qml_component` and use it by composition
instead of inheritance.

``person.qml`` defines a ``Person`` type with ``name`` and ``age``
properties, a ``birthdayHappened`` signal, and a ``celebrateBirthday``
method. The Python ``Employee`` class composes a ``Person`` instance,
connects to its signal, and calls its method:

.. literalinclude:: main.py
    :lines: 19-31
