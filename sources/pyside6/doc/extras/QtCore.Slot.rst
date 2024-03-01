.. currentmodule:: PySide6.QtCore
.. py:decorator:: Slot([type1 [, type2...]] [, name="" [, result=None, [tag=""]]])

   :param name: str
   :param result: type
   :param tag: str

``Slot`` takes a list of Python types of the arguments.

The optional named argument ``name`` defines the slot name. If nothing is
passed, the slot name will be the decorated function name.

The optional named argument ``result`` specifies the return type.

The optional named argument ``tag`` specifies a value to be returned
by ``QMetaMethod.tag()``.

This implementation is functionally compatible with the PyQt one.

=======  ===========  ======
Module   PyQt         PySide
=======  ===========  ======
QtCore   pyqtSignal   Signal
QtCore   pyqtSlot     Slot
=======  ===========  ======

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
