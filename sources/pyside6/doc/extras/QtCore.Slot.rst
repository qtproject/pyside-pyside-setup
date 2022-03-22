.. currentmodule:: PySide6.QtCore
.. _Slot:

Slot
****

Detailed Description
--------------------

    PySide6 adopt PyQt's new signal and slot syntax as-is. The PySide6
    implementation is functionally compatible with the PyQt one, with the
    exceptions listed below.

    PyQt's new signal and slot style utilizes method and decorator names
    specific to their implementation. These will be generalized according to
    the table below:

    =======  =======================  =============
    Module   PyQt factory function    PySide class
    =======  =======================  =============
    QtCore   pyqtSignal               Signal
    QtCore   pyqtSlot                 Slot
    =======  =======================  =============

    .. class:: PySide6.QtCore.Slot([type1 [, type2...]] [, name="" [, result=None]])

            :param name: str
            :param result: type

    ``Slot`` takes a list of Python types of the arguments.

    The optional named argument ``name`` defines the slot name. If nothing is
    passed, the slot name will be the decorated function name.

    The optional named argument ``result`` specifies the return type.

    .. seealso:: :ref:`signals-and-slots`

Q_INVOKABLE
-----------

    There is no equivalent of the Q_INVOKABLE macro of Qt
    since PySide6 slots can actually have return values.
    If you need to create a invokable method that returns some value,
    declare it as a slot, e.g.:

    ::

        class Foo(QObject):

            @Slot(float, result=int)
            def getFloatReturnInt(self, f):
                return int(f)
