.. currentmodule:: PySide6.QtCore

.. py:class:: Signal

    Synopsis
    --------

    Methods
    ^^^^^^^

    .. container:: function_list

        * def :meth:`connect`
        * def :meth:`disconnect`
        * def :meth:`emit`

    Detailed Description
    --------------------

    The :class:`~.Signal` class provides a way to declare and connect Qt
    signals in a pythonic way.

    .. seealso:: :ref:`tutorial_signals_and_slots`

    .. py:method:: __init__([type1 [, type2...]] [, name="" [, arguments=[]]])

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

    .. py:method:: connect(receiver[, type=Qt.AutoConnection])

        :param receiver: Python callable, :deco:`Slot` or :class:`Signal`
        :param type: :class:`~PySide6.QtCore.Qt.ConnectionType`

    Create a connection between this signal and a `receiver`.

    ..  py:method:: disconnect(receiver)

        :param receiver: Python callable, :deco:`Slot` or :class:`Signal`

    Disconnect this signal from the `receiver`.

    .. py:method:: emit(*args)

    Emits the signal. `args` is the arguments to pass to any connected slots,
    if any.
