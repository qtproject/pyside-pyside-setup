.. py:module:: Shiboken

    .. |maya| unicode:: Maya U+2122

    .. _shiboken-module:

    Shiboken module
    ***************

    Functions
    ^^^^^^^^^

    .. container:: function_list

        *    :py:func:`isValid`
        *    :py:func:`wrapInstance`
        *    :py:func:`getCppPointer`
        *    :py:func:`delete`
        *    :py:func:`ownedByPython`
        *    :py:func:`createdByPython`
        *    :py:func:`dump`
        *    :py:func:`disassembleFrame`
        *    :py:func:`dumpTypeGraph`
        *    :py:func:`dumpWrapperMap`
        *    :py:func:`dumpConverters`

    Classes
    ^^^^^^^

    .. container:: class_list

        *    :py:class:`VoidPtr`

    Detailed description
    ^^^^^^^^^^^^^^^^^^^^

    This Python module can be used to access internal information related to our
    binding technology. Access to this internal information is required to e.g.:
    integrate PySide with Qt based programs that offer Python scripting like |maya|
    or just for debug purposes.

    Some function description refer to "Shiboken based objects", which means
    Python objects instances of any Python Type created using Shiboken.

    To import the module:

    .. code-block:: python

        from shiboken6 import Shiboken

    .. py:function:: isValid(obj: object) -> bool

        Given a Python object, returns True if the object methods can be called
        without an exception being thrown. A Python wrapper becomes invalid when
        the underlying C++ object is destroyed or unreachable.

        :param obj: Python object to validate.

    .. py:function:: wrapInstance(address: int, python_type: type) -> Shiboken.object

        Creates a Python wrapper for a C++ object instantiated at a given memory
        address - the returned object type will be the same given by the user.

        The type must be a Python type. The C++ object will not be
        destroyed when the returned Python object reach zero references.

        If the address is invalid or doesn't point to a C++ object of given type
        the behavior is undefined.

        :param int address: Address of the C++ object.
        :param type python_type: Python type for the corresponding C++ object.

    .. py:function:: getCppPointer(obj: Shiboken.object) -> tuple[int, ...]

        Returns a tuple of longs that contain the memory addresses of the
        C++ instances wrapped by the given object.

        :param obj: Shiboken object.

    .. py:function:: delete(obj: Shiboken.object)

        Deletes the C++ object wrapped by the given Python object.

        :param obj: Shiboken object.

    .. py:function:: ownedByPython(obj: Shiboken.object) -> bool

        Given a Shiboken object, returns True if Python is responsible for deleting
        the underlying C++ object, False otherwise.

        If the object was not a Shiboken based object, a TypeError is
        thrown.

        :param obj: Shiboken object.

    .. py:function:: createdByPython(obj: Shiboken.object) -> bool

        Returns true if the given Python object was created by Python.

        :param obj: Shiboken object.

    .. py:function:: dump(obj: object) -> str

        Returns a string with implementation-defined information about the
        object.
        This method should be used **only** for debug purposes by developers
        creating their own bindings as no guarantee is provided that
        the string format will be the same across different versions.

        If the object is not a Shiboken based object, a message is printed.

        :param obj: Python object.

    .. py:function:: disassembleFrame(label: str)

        Prints the current executing Python frame to stdout and flushes.
        The disassembly is decorated by some label. Example:

        .. code-block:: python

            lambda: 42

        is shown from inside C++ as

        .. code-block:: c

            <label> BEGIN
            1           0 LOAD_CONST               1 (42)
                        2 RETURN_VALUE
            <label> END

        When you want to set a breakpoint at the `disassembleFrame` function
        and you use it from C++, you use the pure function name.

        When you want to use it from Python, you can insert it into your Python
        code and then maybe instead set a breakpoint at `SbkShibokenModule_disassembleFrame`
        which is the generated wrapper.

        `label` is a simple string in C++. In Python, you can use any object;
        internally the `str` function is called with it.

        This method should be used **only** for debug purposes by developers.

        :param label: Python string.

    .. py:function:: dumpTypeGraph(file_name: str) -> bool

        Dumps the inheritance graph of the types existing in libshiboken
        to ``.dot`` file for use with `Graphviz <https://graphviz.org/>`_.

        :param file_name: Name of the file to write the graph.

    .. py:function:: dumpWrapperMap()

        Dumps the map of wrappers existing in libshiboken to standard error.

    .. py:function:: dumpConverters()

        Dumps the map of named converters existing in libshiboken to standard
        error.

    .. py:class:: VoidPtr(address, size = -1, writeable = 0)

        :param address: (PyBuffer, SbkObject, int, VoidPtr)
        :param size: int
        :param writeable: int

        Represents a chunk of memory by address and size and implements the ``buffer`` protocol.
        It can be constructed from a ``buffer``, a Shiboken based object, a memory address
        or another VoidPtr instance.

        .. py:method:: toBytes()

            :rtype: bytes

            Returns the contents as ``bytes``.
