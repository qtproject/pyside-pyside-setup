.. _builtin-types:

Built-in Types
--------------

.. _primitive-cpp-types:

Primitive C++ Types
^^^^^^^^^^^^^^^^^^^

Shiboken knows the C++ primitive types like int and float and gathers
information about typedefs like `int32_t` and `size_t` at runtime while
parsing C++ headers. Function overloads using these types will be
automatically generated. To suppress a primitive type, use the
:ref:`rejection` tag.

In principle, there is no need to specify them in the typesystem
file using the :ref:`primitive-type` tag.

However, specifying a type means that the type name is used for
matching signatures of functions for :ref:`modification <modify-function>`.
So, it might make sense to specify architecture-dependent types like `size_t`
to avoid having to spell out the resolved type, which might differ depending
on platform.

`std::string`, `std::wstring` and their associated view types
`std::string_view`, `std::wstring_view` are also supported.

.. _cpython-types:

CPython Types
^^^^^^^^^^^^^

Python types like `str` match types like `PyUnicode` in the *Concrete Objects
Layer* of CPython. They have check functions like `PyUnicode_Check()`, which
Shiboken generates into the code checking the function arguments.

These types occur as parameters when :ref:`adding functions <add-function>`
or :ref:`modifying types <replace-type>`, as type on `add-conversion`
within a :ref:`conversion-rule` or as target language API types on
:ref:`primitive-type`.

They are built into Shiboken as :ref:`custom types <custom-type>` along
with their check functions.
