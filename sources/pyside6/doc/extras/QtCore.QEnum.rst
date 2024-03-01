.. currentmodule:: PySide6.QtCore
.. py:decorator:: QEnum

This class decorator is equivalent to the `Q_ENUM` macro from Qt. The decorator
is used to register a Python Enum derived class to the meta-object system,
which is available via `QObject.staticMetaObject`. The enumerator must be in a
QObject derived class to be registered.

Example
-------

::

    from enum import Enum, auto

    from PySide6.QtCore import QEnum, QObject

    class Demo(QObject):

        @QEnum
        class Orientation(Enum):
            North, East, South, West = range(4)

See :deco:`QFlag` for registering Python Flag derived classes.

Meanwhile all enums and flags have been converted to Python Enums
(default since ``PySide 6.4``), see the :ref:`NewEnumSystem` section.
