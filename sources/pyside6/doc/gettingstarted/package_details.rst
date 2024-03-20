.. _package_details:

Package Details
===============

Having a large project as the Qt Framework available from one simple
installation line::

    pip install pyside6

is really beneficial,
but it might be confusing to newcomers.

Besides your IDE, you don't need to install anything else to develop your
Qt application, because the same command installs many tools
that will help you design UIs, use QML types, generate
files automatically, translate applications, etc.

Package Dependencies
--------------------

.. image:: packages.png
   :width: 400
   :alt: Packages structure and dependency

Starting from 6.3.0, the ``pyside6`` package (wheel) is almost empty,
and only includes references to other packages that are required
to properly use all the modules.
This packages are:

* ``pyside6-essentials``, `essential Qt modules <https://pypi.org/project/PySide6-Essentials/>`_,
* ``pyside6-addons``, `additional Qt modules <https://pypi.org/project/PySide6-Addons/>`_,
* ``shiboken6``, a utility Python module.

You can verify this by running ``pip list`` to check the installed
packages in your Python (virtual) environment::

  (env) % pip list
  Package            Version
  ------------------ -------
  pip                22.0.4
  PySide6            6.3.0
  PySide6-Addons     6.3.0
  PySide6-Essentials 6.3.0
  setuptools         58.1.0
  shiboken6          6.3.0

Both ``pyside6-essentials`` and ``pyside6-addons`` contain Qt binaries
(``.so``, ``.dll``, or ``.dylib``) that are used by the Python wrappers
that enable you to use the Qt modules from Python.
For example, in the ``QtCore`` module, you will find
on Linux:

* ``PySide6/QtCore.abi3.so``, and
* ``PySide6/Qt/lib/libQt6Core.so.6``

inside the ``site-packages`` directory of your (virtual) environment.
The first is the *importable* module which depends on the second file
which is the original QtCore library.

.. note:: The package ``shiboken6-generator`` is not a dependency,
   and it's not available on PyPi. The reason, is that it depends on
   ``libclang``, which is a large library that we don't package, and
   requires a special configuration for you to use. Check the `Shiboken
   Documentation`_ for more details.

..
  Adding the full URL because it's a different sphinx project.
.. _`Shiboken Documentation`: https://doc.qt.io/qtforpython/shiboken6/gettingstarted.html

Tools Included
--------------

PySide6 comes bundled with a set of tools that assist in making the development experience with
PySide6 more efficient. The list of tools can be found :ref:`here <package_tools>`.
