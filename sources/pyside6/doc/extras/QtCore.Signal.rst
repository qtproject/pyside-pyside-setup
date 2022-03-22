.. currentmodule:: PySide6.QtCore
.. _Signal:

Signal
******

Synopsis
--------

Functions
^^^^^^^^^

+---------------------------------------------------------------------------------------------+
|def :meth:`connect<Signal.connect>` (receiver)                                               |
+---------------------------------------------------------------------------------------------+
|def :meth:`disconnect<Signal.disconnect>` (receiver)                                         |
+---------------------------------------------------------------------------------------------+
|def :meth:`emit<Signal.disconnect>` (\*args)                                                 |
+---------------------------------------------------------------------------------------------+

Detailed Description
--------------------

    The :class:`~.Signal` class provides a way to declare and connect Qt
    signals in a pythonic way.

.. class:: PySide6.QtCore.Signal([type1 [, type2...]] [, name="" [, arguments=[]]])

        :param name: str
        :param arguments: list

``Signal`` takes a list of Python types of the arguments.

 It is possible to use the same signal name with different types by
 passing a list of tuples representing the signatures, but this is a legacy
 technique recommended against in new code (see
 :ref:`overloading-signals-and-slots`).

The optional named argument ``name`` defines the signal name. If nothing is
passed, the new signal will have the same name as the variable that it is
being assigned to.

The optional named argument ``arguments`` receives a list of strings
denoting the argument names. This is useful for QML applications which
may refer to the emitted values by name.

.. method:: Signal.connect(receiver[, type=Qt.AutoConnection])

    Create a connection between this signal and a `receiver`, the `receiver`
    can be a Python callable, a :class:`Slot` or a :class:`Signal`.

.. method:: Signal.disconnect(receiver)

    Disconnect this signal from a `receiver`, the `receiver` can be a Python
    callable, a :class:`Slot` or a :class:`Signal`.

.. method:: Signal.emit(*args)

    `args` is the arguments to pass to any connected slots, if any.

.. seealso:: :ref:`signals-and-slots`
