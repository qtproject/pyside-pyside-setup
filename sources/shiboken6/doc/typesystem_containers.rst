.. _opaque-containers:

*****************
Opaque Containers
*****************

Normally, Python containers such as ``list`` or ``dict`` are passed when
calling C++ functions taking a corresponding C++ container (see
:ref:`container-type`).

This means that for each call, the entire Python container is converted to
a C++ container, which can be inefficient when for example creating plots
from lists of points.

To work around this, special opaque containers can generated which wrap an
underlying C++ container directly (currently implemented for ``list`` types).
They implement the sequence protocol and can be passed to the function
instead of a Python list. Manipulations like adding or removing elements
can applied directly to them using the C++ container functions.

This is achieved by specifying the name and the instantiated type
in the ``opaque-containers`` attribute of :ref:`container-type`.

A second use case are public fields of container types. In the normal case,
they are converted to Python containers on read access. By a field modification,
(see :ref:`modify-field`), it is possible to obtain an opaque container
which avoids the conversion and allows for direct modification of elements.

The table below lists the functions supported for opaque sequence containers
besides the sequence protocol (element access via index and ``len()``). Both
the STL and the Qt naming convention (which resembles Python's) are supported:

    +-------------------------------------------+-----------------------------------+
    |Function                                   | Description                       |
    +-------------------------------------------+-----------------------------------+
    | ``push_back(value)``, ``append(value)``   | Appends *value* to the sequence.  |
    +-------------------------------------------+-----------------------------------+
    | ``push_front(value)``, ``prepend(value)`` | Prepends *value* to the sequence. |
    +-------------------------------------------+-----------------------------------+
    | ``clear()``                               | Clears the sequence.              |
    +-------------------------------------------+-----------------------------------+
    | ``pop_back()``, ``removeLast()``          | Removes the last element.         |
    +-------------------------------------------+-----------------------------------+
    | ``pop_front()``, ``removeFirst()``        | Removes the first element.        |
    +-------------------------------------------+-----------------------------------+
