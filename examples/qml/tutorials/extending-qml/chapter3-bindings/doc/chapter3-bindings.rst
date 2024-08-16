Extending QML - Adding Property Bindings
========================================

This is the third of a series of 6 examples forming a tutorial about extending
QML with Python.

Property binding is a powerful feature of QML that allows values of different
types to be synchronized automatically. It uses signals to notify and update
other types' values when property values are changed.

Let's enable property bindings for the ``color`` property. That means if we
have code like this:

.. literalinclude:: app.qml
    :lineno-start: 7
    :lines: 7-40

The ``color: chartA.color`` statement binds the ``color`` value of ``chartB``
to the ``color`` of ``chartA.`` Whenever ``chartA`` 's ``color`` value changes,
``chartB`` 's ``color`` value updates to the same value. When the window is
clicked, the ``onClicked`` handler in the ``MouseArea`` changes the color of
``chartA`` , thereby changing both charts to the color blue.

It's easy to enable property binding for the ``color`` property. We add a
``notify`` parameter to its ``Property`` decorator to indicate that a
``colorChanged`` signal is emitted whenever the value changes.

.. literalinclude:: bindings.py
    :lineno-start: 39
    :lines: 39-39

.. literalinclude:: bindings.py
    :lineno-start: 21
    :lines: 21-26

Then, we emit this signal in ``setColor()``:

.. literalinclude:: bindings.py
    :lineno-start: 43
    :lines: 43-48

It's important for ``setColor()`` to check that the color value has actually
changed before emitting ``colorChanged().`` This ensures the signal is not
emitted unnecessarily and also prevents loops when other types respond to the
value change.

The use of bindings is essential to QML. You should always add ``notify``
signals for properties if they are able to be implemented, so that your
properties can be used in bindings. Properties that cannot be bound cannot be
automatically updated and cannot be used as flexibly in QML. Also, since
bindings are invoked so often and relied upon in QML usage, users of your
custom QML types may see unexpected behavior if bindings are not implemented.
