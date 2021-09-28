.. _builtin-types:

Built-in Types
--------------

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
