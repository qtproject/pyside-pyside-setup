Fixing Type Hints
=================

Overview
--------

If you notice any type hint issues in your project while using mypy with the PySide6 API,
this document provides guidance on how to :ref:`identify<finding-type-hints-issues>`,
correct, and maintain accurate type hints. Improving type hints enhances IDE support, enables
better code completion, and improves static analysis with tools like `mypy`_.

PySide6 uses `Shiboken`_ to generate Python bindings from C++ headers, but:

- Some type hints are missing or too generic (e.g., ``Any``)
- Some are incorrect due to overloads or inheritance issues
- Some APIs are dynamic or wrapped in unusual ways

Fixing these improves developer experience for all users of PySide6.

.. note:: Please refer to our `contribution guideline`_.


Tools and Setup
---------------

To find and fix the type hints ensure that your development environment has PySide6 installed.

.. code-block:: bash

    python -m venv venv
    source venv/bin/activate
    pip install PySide6 mypy

or, the entire PySide6 project can be cloned:

.. code-block:: bash

    git clone https://code.qt.io/pyside/pyside-setup.git
    cd pyside-setup


Finding Type Hints Issues
-------------------------

You can locate the type hints issues using a static analysis tool, such as ``mypy``.

.. code-block:: bash

    mypy your_project/


How to Fix
----------

PySide6 uses `Shiboken`_ to generate bindings, and type information can come from either static
`typesystem`_ XML files or dynamic Python-based signature definitions.

1. Fixing with Typesystem Files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Each Qt module has an associated XML `typesystem`_ (e.g., typesystem_widgets.xml). You can specify
or override type hints using the pyi-type attribute.

Example from typesystem_gui_common.xml:

.. code-block:: xml

    <modify-function signature="inverted(bool*)const">
        <modify-argument index="return" pyi-type="Tuple[PySide6.QtGui.QTransform, bool]">
            <replace-type modified-type="PyTuple"/>
        </modify-argument>
    </modify-function>


2. Fixing with Python Signature Support
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Python scripts located under `shiboken module`_.

Key Files:

- ``enum_sig.py``: Enumerates all signatures of a class
- ``pyi_generator.py``: Generates ``.pyi`` files for arbitrary modules
- ``layout.py``: Configures differently formatted versions of signatures
- ``mapping.py``: Maps the C++ types to Python equivalents
- ``parser.py``: Parses the signature text and creates properties for the signature objects

The Python scripts here are responsible for parsing signature texts, creating signatures, and
applying custom rules to handle special behaviors in the PySide6 API.


Rebuild and Verify
------------------

After modifying `typesystem`_ files or Python signature logic, `rebuild`_ PySide6 to regenerate
``.pyi`` files:

.. code-block:: bash

    python setup.py build --qtpaths=/path/to/qtpaths --parallel=8 --reuse-build


This regenerates the bindings and updates the stub files used for static analysis.

To verify the changes, you can either run ``mypy`` on your own code:

.. code-block:: bash

    mypy your_project/

Or use the dedicated script provided by PySide6 to validate the generated stubs:

.. code-block:: bash

    python sources/pyside6/tests/pysidetest/mypy_correctness_test.py

This tool runs ``mypy`` against the generated stub files to detect type annotation issues and
inconsistencies. It is typically used to validate ``.pyi`` stubs in the build directory after
generation.


Special Cases and Workarounds
-----------------------------

While most type hints in PySide6 are generated automatically through `typesystem`_ XML or parsed
function signatures, there are a number of **special cases** that require manual intervention.

Missing Optional Return Values
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Some functions in the PySide6 stub files are missing ``None`` as a valid return type. This usually
happens when the C++ method returns a pointer, which may be ``nullptr``, but the automatic
generator assumes a non-optional return in Python. To fix these cases, PySide6 maintains a list of
such functions in the `mapping.py`_ file.

Look for the set named:

.. code-block:: python

    missing_optional_return = {}

This is a list of functions where the return type should be wrapped in ``Optional[...]``. These
entries override the default behavior and ensure that the generated ``.pyi`` stub files correctly
reflect that the function may return ``None``.

Char* Argument Mapping
^^^^^^^^^^^^^^^^^^^^^^

In C++, ``char*`` is commonly used to represent both binary data (as ``bytes``) and null-terminated
strings (as ``str``). By default, PySide6 maps ``char*`` to ``bytes`` in type hints.

However, some Qt functions are known to expect text input and should be treated as accepting ``str``
instead. To handle these exceptions, PySide6 overrides the default mapping for specific functions.
This override is defined in the `mapping.py`_ file.

Look for the following logic:

.. code-block:: python

    # Special case - char* can either be 'bytes' or 'str'. The default is 'bytes'.
    # Here we manually set it to map to 'str'.
    type_map_tuple.update({("PySide6.QtCore.QObject.setProperty", "char*"): str})
    type_map_tuple.update({("PySide6.QtCore.QObject.property", "char*"): str})
    type_map_tuple.update({("PySide6.QtCore.QObject.inherits", "char*"): str})
    ...

Each entry is a ``(function_name, argument_type)`` tuple mapped to the correct Python type. This
ensures that generated stubs reflect the expected usage of ``str`` rather than ``bytes``.


.. _mypy: https://pypi.org/project/mypy/
.. _Shiboken: https://doc.qt.io/qtforpython-6/shiboken6/index.html
.. _typesystem: https://doc.qt.io/qtforpython-6/shiboken6/typesystem.html
.. _contribution guideline: https://wiki.qt.io/Qt_Contribution_Guidelines
.. _rebuild: https://doc.qt.io/qtforpython-6/building_from_source/index.html
.. _mapping.py: https://code.qt.io/cgit/pyside/pyside-setup.git/tree/sources/shiboken6/shibokenmodule/files.dir/shibokensupport/signature/mapping.py
.. _shiboken module: https://code.qt.io/cgit/pyside/pyside-setup.git/tree/sources/shiboken6/shibokenmodule/files.dir/shibokensupport/signature
