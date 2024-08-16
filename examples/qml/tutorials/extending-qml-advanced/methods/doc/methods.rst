Extending QML - Methods Example
===============================

This example builds on the :ref:`example_qml_tutorials_extending-qml-advanced_adding`,
the :ref:`example_qml_tutorials_extending-qml-advanced_properties` and
the :ref:`example_qml_tutorials_extending-qml-advanced_advanced2-inheritance-and-coercion`.

The Methods Example has an additional method in the ``BirthdayParty`` class:
``invite()``. ``invite()`` is decorated with ``@Slot`` so that it can be
called from QML.

In ``example.qml``, the ``invite()`` method is called
in the ``QtQml.Component.completed()`` signal handler.
