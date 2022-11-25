.. _whatisshiboken:

Binding Generation: What Is Shiboken?
=====================================

When you install ``PySide6`` you might have notice that also ``Shiboken6``
is installed as a dependency:

.. code-block:: bash

    (env) [qt ~]$ pip install pyside6
    Collecting pyside6
      Downloading PySide6-6.0.0-6.0.0-cp36.cp37.cp38.cp39-abi3-manylinux1_x86_64.whl (170.5 MB)
         |████████████████████████████████| 170.5 MB 42 kB/s
    Collecting shiboken6==6.0.0
      Downloading shiboken6-6.0.0-6.0.0-cp36.cp37.cp38.cp39-abi3-manylinux1_x86_64.whl (964 kB)
         |████████████████████████████████| 964 kB 29.3 MB/s
    Installing collected packages: shiboken6, pyside6
    Successfully installed pyside6-6.0.0 shiboken6-6.0.0

That installed package is also called **Shiboken Module**, and it contains
some utilities for PySide to properly work.
You can find more information about it on its
`documentation page (module) <https://doc.qt.io/qtforpython/shiboken6/shibokenmodule.html>`_

There is a third package that does not get installed when you install PySide,
because it is not required, and it is called **Shiboken Generator**.

Most of the times you see mentions to use "Shiboken" or to do something
related to "binding generation", it is about this third package, and **not**
the dependency of the PySide package.

Do I Need Shiboken Generator?
-----------------------------

If your goal is to just write Qt applications in Python,
you do not need to worry about a Shiboken generator installation,
but on the other hand, if you want to work with your own bindings
or extend Qt/C++ applications with Python, you **need** it.

You can find all the information related to Shiboken on its
`documentation page (generator) <https://doc.qt.io/qtforpython/shiboken6/>`_.
