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

Getters returning references can also be modified to return opaque containers.
This is done by modifying the return type to the name of the opaque container
(see :ref:`replace-type`).

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
    | ``reserve(size)``                         | For containers that support it    |
    |                                           | (``std::vector``, ``QList``),     |
    |                                           | allocate memory for at least      |
    |                                           | ``size`` elements, preventing     |
    |                                           | reallocations.                    |
    +-------------------------------------------+-----------------------------------+
    | ``capacity()``                            | For containers that support it    |
    |                                           | (``std::vector``, ``QList``),     |
    |                                           | return the number of elements     |
    |                                           | that can be stored without        |
    |                                           | reallocation.                     |
    +-------------------------------------------+-----------------------------------+
    | ``data()``                                | For containers that support it    |
    |                                           | (``std::vector``, ``QList``),     |
    |                                           | return a buffer viewing the       |
    |                                           | memory.                           |
    +-------------------------------------------+-----------------------------------+
    | ``constData()``                           | For containers that support it    |
    |                                           | (``std::vector``, ``QList``),     |
    |                                           | return a read-only buffer viewing |
    |                                           | the memory.                       |
    +-------------------------------------------+-----------------------------------+

Following is an example on creating an opaque container named ``IntVector``
from `std::vector<int>`, and using it in Python.

We will consider three separate use cases.

**Case 1** - When a Python list is passed to C++ function
`TestOpaqueContainer.getVectorSum(const std::vector<int>&)` as an opaque container

.. code-block:: c

    class TestOpaqueContainer
    {
    public:
        static int getVectorSum(const std::vector<int>& intVector)
        {
            return std::accumulate(intVector.begin(), intVector.end(), 0);
        }
    };

**Case 2** - When we have a C++ class named `TestOpaqueContainer` with a `std::vector<int>`
public variable

.. code-block:: c

    class TestOpaqueContainer
    {
    public:
        std::vector<int> intVector;

    };

**Case 3** - When we have a C++ class named `TestOpaqueContainer` with a `std::vector<int>` as
private variable and the variable is returned by a reference through a getter.

.. code-block:: c

    class TestOpaqueContainer
    {
    public:
        std::vector<int>& getIntVector()
        {
            return this->intVector;
        }

    private:
        std::vector<int> intVector;

    };

.. note:: Cases 2 and 3 are generally considered to be bad class design in C++. However, the purpose
          of these examples are rather to show the different possibilities with opaque containers in
          Shiboken than the class design.

In all the three cases, we want to use `intVector` in Python through an opaque-container. The
first thing to do is to create the corresponding `<container-type />` attribute in the typesystem
file, making Shiboken aware of the `IntVector`.

.. code-block:: xml

    <container-type name="std::vector" type="vector" opaque-containers="int:IntVector">
        <include file-name="vector" location="global"/>
        <conversion-rule>
            <native-to-target>
                <insert-template name="shiboken_conversion_cppsequence_to_pylist"/>
            </native-to-target>
            <target-to-native>
                <add-conversion type="PySequence">
                    <insert-template name="shiboken_conversion_pyiterable_to_cppsequentialcontainer"/>
                </add-conversion>
            </target-to-native>
        </conversion-rule>
    </container-type>

For the rest of the steps, we consider the three cases separately.

**Case 1** - When a Python list is passed to a C++ function

As the next step, we create a typesystem entry for the class `TestOpaqueContainer`.

.. code-block:: xml

    <value-type name="TestOpaqueContainer" />

In this case, the typesystem entry is simple and the function
`getVectorSum(const std::vector<int>&)` accepts `IntVector` as the parameter. This is
because inherantly `IntVector` is the same as `std::vector<int>`.

Now, build the code to create the \*_wrapper.cpp and \*.so files which we import into Python.

Verifying the usage in Python

.. code-block:: bash

    >>> vector = IntVector()
    >>> vector.push_back(2)
    >>> vector.push_back(3)
    >>> len(vector)
    2
    >>> TestOpaqueContainer.getVectorSum(vector)
    vector sum is 5

**Case 2** - When the variable is public

We create a typesystem entry for the class `TestOpaqueContainer`.

.. code-block:: xml

    <value-type name="TestOpaqueContainer">
        <modify-field name="intVector" opaque-container="yes"/>
    </value-type>

In the `<modify-field />` notice the `opaque-container="yes"`. Since the type
of `intVector' is `std::vector<int>`, it picks up the ``IntVector`` opaque
container.

Build the code to create the \*_wrapper.cpp and \*.so files which we import into Python.

Verifying the usage in Python

.. code-block:: bash

    >>> test = TestOpaqueContainer()
    >>> test
    <Universe.TestOpaqueContainer object at 0x7fe17ef30c30>
    >>> test.intVector.push_back(1)
    >>> test.intVector.append(2)
    >>> len(test.intVector)
    2
    >>> test.intVector[1]
    2
    >>> test.intVector.removeLast()
    >>> len(test.intVector)
    1

**Case 3** - When the variable is private and returned by reference through a getter

Similar to the previous cases, we create a typesystem entry for the class `TestOpaqueContainer`.

.. code-block:: xml

    <value-type name="TestOpaqueContainer">
        <modify-function signature="getIntVector()">
            <modify-argument index="return">
                <replace-type modified-type="IntVector" />
            </modify-argument>
        </modify-function>
    </value-type>

In this case, we specify the name of the opaque container `IntVector` in the <replace-type />
field.

Build the code to create the \*_wrapper.cpp and \*.so files which we import into Python.

Verifying the usage in Python

.. code-block:: bash

    >>> test = TestOpaqueContainer()
    >>> test
    <Universe.TestOpaqueContainer object at 0x7f62b9094c30>
    >>> vector = test.getIntVector()
    >>> vector
    <Universe.IntVector object at 0x7f62b91f7d00>
    >>> vector.push_back(1)
    >>> vector.push_back(2)
    >>> len(vector)
    2
    >>> vector[1]
    2
    >>> vector.removeLast()
    >>> len(vector)
    1

In all the three cases, if we check out the corresponding wrapper class for the module, we will see
the lines

.. code-block:: c

    static PyMethodDef IntVector_methods[] = {
        {"push_back", reinterpret_cast<PyCFunction>(
            ShibokenSequenceContainerPrivate<std::vector<int >>::push_back),METH_O, "push_back"},
        {"append", reinterpret_cast<PyCFunction>(
            ShibokenSequenceContainerPrivate<std::vector<int >>::push_back),METH_O, "append"},
        {"clear", reinterpret_cast<PyCFunction>(
            ShibokenSequenceContainerPrivate<std::vector<int >>::clear), METH_NOARGS, "clear"},
        {"pop_back", reinterpret_cast<PyCFunction>(
            ShibokenSequenceContainerPrivate<std::vector<int >>::pop_back), METH_NOARGS,
            "pop_back"},
        {"removeLast", reinterpret_cast<PyCFunction>(
            ShibokenSequenceContainerPrivate<std::vector<int >>::pop_back), METH_NOARGS,
            "removeLast"},
        {nullptr, nullptr, 0, nullptr} // Sentinel
    };

This means, the above mentioned methods are available to be used in Python with the ``IntVector``
opaque container.

.. note:: `Plot example <https://doc.qt.io/qtforpython/examples/example_widgets_painting_plot.html>`_
          demonstrates an example of using an opaque container `QPointList`, which wraps a C++
          `QList<QPoint>`. The corresponding typesystem file where QPointList can be found `here
          <https://code.qt.io/cgit/pyside/pyside-setup.git/tree/sources/pyside6/PySide6/QtCore/typesystem_core_common.xml>`_

