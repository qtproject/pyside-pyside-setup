.. _qml-methods-example:

Extending QML - Methods Example
===============================

This example builds on the :ref:`qml-adding-types-example`,
the :ref:`qml-object-and-list-property-types-example` and
the :ref:`qml-inheritance-and-coercion-example`.

The Methods Example has an additional method in the ``BirthdayParty`` class:
``invite()``. ``invite()`` is decorated with ``@Slot`` so that it can be
called from QML.

In ``example.qml``, the ``invite()`` method is called
in the ``QtQml.Component.completed()`` signal handler.
