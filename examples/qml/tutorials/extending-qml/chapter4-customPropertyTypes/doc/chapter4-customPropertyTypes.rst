Extending QML - Using Custom Property Types
===========================================

This is the fourth of a series of 6 examples forming a tutorial about extending
QML with Python.

The ``PieChart`` type currently has a string-type property and a color-type property.
It could have many other types of properties. For example, it could have an
int-type property to store an identifier for each chart:

.. code-block:: python

    class PieChart(QQuickPaintedItem):
        chartIdChanged = Signal()

        @Property(int, notify=chartIdChanged)
        def chartId(self):
            pass

        @chartId.setter
        def setChartId(self, chartId):
            pass

.. code-block:: javascript

    // QML
    PieChart {
        ...
        chartId: 100
    }

Aside from ``int``, we could use various other property types. Many of the Qt
data types such as ``QColor``, ``QSize`` and ``QRect`` are automatically
supported from QML.

If we want to create a property whose type is not supported by QML by default,
we need to register the type with the QML engine.

For example, let's replace the use of the ``property`` with a type called
``PieSlice`` that has a ``color`` property. Instead of assigning a color,
we assign an ``PieSlice`` value which itself contains a ``color``:

.. literalinclude:: app.qml
    :lineno-start: 4
    :lines: 4-22

Like ``PieChart``, this new ``PieSlice`` type inherits from
``QQuickPaintedItem``, is exposed via the ``QmlElement`` decorator and declares
its properties with the ``Property`` decorator:

.. literalinclude:: customPropertyTypes.py
    :lineno-start: 21
    :lines: 21-40

To use it in ``PieChart``, we modify the ``color`` property declaration
and associated method signatures:

.. literalinclude:: customPropertyTypes.py
    :lineno-start: 58
    :lines: 58-65

There is one thing to be aware of when implementing ``setPieSlice()``. The
``PieSlice`` is a visual item, so it must be set as a child of the ``PieChart``
using ``QQuickItem.setParentItem()`` so that the ``PieChart`` knows to paint
this child item when its contents are drawn.

As with ``PieChart``, we add the ``Charts`` type namespace, version 1.0:

.. literalinclude:: customPropertyTypes.py
    :lineno-start: 15
    :lines: 15-18
