Extending QML (advanced) - Grouped Properties
=============================================

This is the fourth of a series of 6 examples forming a tutorial using the
example of a birthday party to demonstrate some of the advanced features of
QML.

More information is needed about the shoes of the guests. Aside from their
size, we also want to store the shoes' color, brand, and price. This
information is stored in a ``ShoeDescription`` class.

.. literalinclude:: person.py
    :lineno-start: 14
    :lines: 14-66

Each person now has two properties, a ``name`` and a shoe description ``shoe``.

.. literalinclude:: person.py
    :lineno-start: 69
    :lines: 69-90

Specifying the values for each element of the shoe description works but is a
bit repetitive.

.. literalinclude:: People/Main.qml
    :lineno-start: 26
    :lines: 26-32

Grouped properties provide a more elegant way of assigning these properties.
Instead of assigning the values to each property one-by-one, the individual
values can be passed as a group to the ``shoe`` property making the code more
readable. No changes are required to enable this feature as it is available by
default for all of QML.

.. literalinclude:: People/Main.qml
    :lineno-start: 9
    :lines: 9-12
