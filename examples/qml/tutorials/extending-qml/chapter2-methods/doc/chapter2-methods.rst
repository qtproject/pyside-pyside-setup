Extending QML - Connecting to C++ Methods and Signals
=====================================================

This is the second of a series of 6 examples forming a tutorial about extending
QML with Python.

Suppose we want ``PieChart`` to have a ``clearChart()`` method that erases the
chart and then emits a ``chartCleared`` signal. Our ``app.qml`` would be able
to call ``clearChart()`` and receive ``chartCleared()`` signals like this:

.. literalinclude:: app.qml
    :lineno-start: 4
    :lines: 4-32

To do this, we add a ``clearChart()``  method and a ``chartCleared()``  signal
to our C++ class:

.. literalinclude:: methods.py
    :lineno-start: 54
    :lines: 54-58

The use of the ``Slot`` decorator makes the ``clearChart()`` method available
to the Qt Meta-Object system, and in turn, to QML. The method simply changes
the color to ``Qt::transparent``, repaints the chart, then emits the
``chartCleared()`` signal:

.. literalinclude:: methods.py
    :lineno-start: 21
    :lines: 21-24

Now when we run the application and click the window, the pie chart disappears,
and the application outputs::

    qml: The chart has been cleared
