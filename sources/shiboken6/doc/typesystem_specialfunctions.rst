.. _special-functions:

Special functions
-----------------

.. _sequence-protocol:

Sequence Protocol
^^^^^^^^^^^^^^^^^

Support for the sequence protocol is achieved adding functions with special
names, this is done using the :ref:`add-function` tag.

The special function names are:

    ============= =============================================== ==================== ===================
    Function name Parameters                                      Return type          CPython equivalent
    ============= =============================================== ==================== ===================
    __len__       PyObject* self                                  Py_ssize_t           PySequence_Size
    __getitem__   PyObject* self, Py_ssize_t _i                   PyObject*            PySequence_GetItem
    __setitem__   PyObject* self, Py_ssize_t _i, PyObject* _value int                  PySequence_SetItem
    __contains__  PyObject* self, PyObject* _value                int                  PySequence_Contains
    __concat__    PyObject* self, PyObject* _other                PyObject*            PySequence_Concat
    ============= =============================================== ==================== ===================

You just need to inform the function name to the :ref:`add-function` tag, without any
parameter or return type information, when you do it, |project| will create a C
function with parameters and return type defined by the table above.

The function needs to follow the same semantics of the *CPython equivalent*
function, the only way to do it is using the
:ref:`inject-code <codeinjectionsemantics>` tag.

A concrete example how to add sequence protocol support to a class can be found
on shiboken tests, more precisely in the definition of the Str class in
``tests/samplebinding/typesystem_sample.xml``.

.. _bool-cast:

Bool Cast
^^^^^^^^^

Implementing bool casts enables using values which have a concept of validity
in boolean expressions. In C++, this is commonly implemented as
``operator bool() const``. In Qt, relevant classes have a
``bool isNull() const`` function.

In Python, the function ``__bool__`` is used for this. shiboken can generate
this functions depending on the command line options
:ref:`--use-operator-bool-as-nb_nonzero <use-operator-bool-as-nb-nonzero>`
and :ref:`--use-isnull-as-nb_nonzero <use-isnull-as-nb-nonzero>`,
which can be overridden by specifying the boolean attributes
**isNull** or **operator-bool** on the :ref:`value-type` or :ref:`object-type`
elements in typesystem XML.
