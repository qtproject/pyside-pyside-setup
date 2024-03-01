.. currentmodule:: PySide6.QtCore
.. py:decorator:: QFlag

QFlag handles a variation of the Python Enum, the Flag class.

Please do not confuse that with the Qt QFlags concept. Python does
not use that concept, it has its own class hierarchy, instead.
For more details, see the `Python enum documentation <https://docs.python.org/3/library/enum.html>`_.

Example
-------

::

    from enum import Flag, auto

    from PySide6.QtCore import QFlag, QObject

    class Demo(QObject):

        @QFlag
        class Color(Flag):
            RED = auto()
            BLUE = auto()
            GREEN = auto()
            WHITE = RED | BLUE | GREEN


Details about Qt Flags:
-----------------------

There are some small differences between Qt flags and Python flags.
In Qt, we have for instance these declarations:

::

    enum    QtGui::RenderHint { Antialiasing, TextAntialiasing, SmoothPixmapTransform,
                                HighQualityAntialiasing, NonCosmeticDefaultPen }
    flags   QtGui::RenderHints

The equivalent Python notation would look like this:

::

    @QFlag
    class RenderHints(enum.Flag)
        Antialiasing = auto()
        TextAntialiasing = auto()
        SmoothPixmapTransform = auto()
        HighQualityAntialiasing = auto()
        NonCosmeticDefaultPen = auto()


As another example, the Qt::AlignmentFlag flag has 'AlignmentFlag' as the enum
name, but 'Alignment' as the type name. Non flag enums have the same type and
enum names.

::

    enum Qt::AlignmentFlag
    flags Qt::Alignment

The Python way to specify this would be

::

    @QFlag
    class Alignment(enum.Flag):
        ...

See :deco:`QEnum` for registering Python Enum derived classes.

Meanwhile all enums and flags have been converted to Python Enums
(default since ``PySide 6.4``), see the :ref:`NewEnumSystem` section.
