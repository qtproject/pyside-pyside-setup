Extending QML - Using List Property Types
=========================================

This is the fifth of a series of 6 examples forming a tutorial about extending
QML with Python.

Right now, a ``PieChart`` can only have one ``PieSlice.`` Ideally a chart would
have multiple slices, with different colors and sizes. To do this, we could
have a ``slices`` property that accepts a list of ``PieSlice`` items:

.. literalinclude:: app.qml
   :lineno-start: 4
   :lines: 4-32

To do this, we replace the ``pieSlice`` property in ``PieChart`` with a
``slices`` property, declared as a class variable of the
:class:`~PySide6.QtQml.ListProperty` type.
The ``ListProperty`` class enables the creation of list properties in
QML extensions. We replace the ``pieSlice()`` function with a ``slices()``
function that returns a list of slices, and add an internal ``appendSlice()``
function (discussed below). We also use a list to store the internal list of
slices as ``_slices``:

.. literalinclude:: listproperties.py
   :lineno-start: 62
   :lines: 62-65

.. literalinclude:: listproperties.py
   :lineno-start: 75
   :lines: 75-79

Although the ``slices`` property does not have an associated setter, it is
still modifiable because of the way ``ListProperty`` works. We indicate
that the internal ``PieChart.appendSlice()`` function is to be called whenever
a request is made from QML to add items to the list.

The ``appendSlice()`` function simply sets the parent item as before, and adds
the new item to the ``_slices`` list. As you can see, the append function for
a ``ListProperty`` is called with two arguments: the list property, and the
item that is to be appended.

The ``PieSlice`` class has also been modified to include ``fromAngle`` and
``angleSpan`` properties and to draw the slice according to these values. This
is a straightforward modification if you have read the previous pages in this
tutorial, so the code is not shown here.
