.. _pysideapi2:

|project| Considerations
========================

API Changes
-----------

One of the goals of |pymodname| is to be API compatible with PyQt,
with certain exceptions.

The latest considerations and known issues will be also reported
in the `wiki <https://wiki.qt.io/Qt_for_Python/Considerations>`_.

__hash__() function return value
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The hash value returned for the classes :class:`PySide6.QtCore.QDate`,
:class:`PySide6.QtCore.QDateTime`, :class:`PySide6.QtCore.QTime`, :class:`PySide6.QtCore.QUrl`
will be based on their string representations, thus objects with the same value will produce the
same hash.


QString
~~~~~~~

Methods and functions that change the contents of a QString argument were modified to receive an
immutable Python Unicode (or str) and return another Python Unicode/str as the modified string.

The following methods had their return types modified this way:

**Classes:** QAbstractSpinBox, QDateTimeEdit, QDoubleSpinBox, QSpinBox, QValidator

* ``fixup(string): string``
* ``validate(string, int): [QValidator.State, string, int]``

**Classes:** QDoubleValidator, QIntValidator, QRegExpValidator

* ``validate(string, int): [QValidator.State, string, int]``

**Class:** QClipboard

* ``text(string, QClipboard.Mode mode=QClipboard.Clipboard): [string, string]``

**Class:** QFileDialog

Instead of ``getOpenFileNameAndFilter()``, ``getOpenFileNamesAndFilter()`` and
``getSaveFileNameAndFilter()`` like PyQt does, PySide has modified the original methods to return
a tuple.

* ``getOpenFileName(QWidget parent=None, str caption=None, str dir=None, str filter=None, QFileDialog.Options options=0): [string, filter]``
* ``getOpenFileNames(QWidget parent=None, str caption=None, str dir=None, str filter=None, QFileDialog.Options options=0): [list(string), filter]``
* ``getSaveFileName(QWidget parent=None, str caption=None, str dir=None, str filter=None, QFileDialog.Options options=0): [string, filter]``

**Class:** QWebPage

* ``javaScriptPrompt(QWebFrame, string, string): [bool, string]``

**Classes:** QFontMetrics and QFontMetricsF

They had two new methods added. Both take a string of one character and convert to a QChar
(to call the C++ counterpart):

* ``widthChar(string)``
* ``boundingRectChar(string)``


QTextStream
~~~~~~~~~~~

Inside this class some renames were applied to avoid clashes with native Python functions.
They are: ``bin_()``, ``hex_()`` and ``oct_()``.
The only modification was the addition of the '_' character.


QVariant
~~~~~~~~

As ``QVariant`` was removed, any function expecting it can receive any Python object (``None`` is
an invalid ``QVariant``).
The same rule is valid when returning something: the returned ``QVariant`` will be converted to
its original Python object type.

When a method expects a ``QVariant::Type`` the programmer can use a string (the type name) or the
type itself.


qApp "macro"
~~~~~~~~~~~~

The C++ API of QtWidgets provides a macro called ``qApp`` that roughly expands to
``QtWidgets::QApplication->instance()``.

In PySide, we tried to create a macro-like experience.
For that, the ``qApp`` variable was implemented as a normal variable
that lives in the builtins.
After importing ``PySide6``, you can immediately use ``qApp``.

As a useful shortcut for the action "create an application if it was not created", we recommend::

    qApp or QtWidgets.QApplication()

or if you want to check if there is one, simply use the truth value::

    if qApp:
        # do something if an application was created
        pass

Comparing to ``None`` is also possible, but slightly over-specified.


Testing support
+++++++++++++++

For testing purposes, you can also get rid of the application by calling::

    qApp.shutdown()

As for 5.14.2, this is currently an experimental feature that is not fully tested.


Embedding status
++++++++++++++++

In embedded mode, application objects that are pre-created in C++ don't have a Python wrapper.
The ``qApp`` variable is created together with a wrapped application.
Therefore, ``qApp`` does not exist in that embedded mode.
Please note that you always can use ``QtWidgets.QApplication.instance()`` instead.


Abandoned Alternative
+++++++++++++++++++++

We also tried an alternative implementation with a ``qApp()`` function that was more *pythonic*
and problem free, but many people liked the ``qApp`` macro better for its brevity, so here it is.


Rich Comparison
~~~~~~~~~~~~~~~

There was a long-standing bug in the ``tp_richcompare`` implementation of PySide classes.

* When a class did not implement it, the default implementation of ``object`` is used.
  This implements ``==`` and ``!=`` like the ``is`` operator.

* When a class implements only a single function like ``<``, then the default implementation
  was disabled, and expressions like ``obj in sequence`` failed with ``NotImplemented``.

This oversight was fixed in version 5.15.1 .


|project| Features
==================

In |project|, we begin for the first time to support a more pythonic user interface.
With a special import statement, you can switch on features which replace certain aspects of
the Python interpreter. This is done by an import statement right after the PySide6 import.

snake_case
----------

With the statement:

.. code-block:: python

    from __feature__ import snake_case

all methods in the current module are switched from ``camelCase`` to ``snake_case``.
A single upper case letter is replaced by an underscore and the lower case letter.

true_property
-------------

With the statement:

.. code-block:: python

    from __feature__ import true_property

all getter and setter functions which are marked as a property in the Qt6 docs
are replaced by Python property objects. Properties are also listed as such
in the according QMetaObject of a class.

Example for both features
-------------------------

Some |project| snippet might read:

.. code-block:: python

    self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

With the above features selected, this reads:

.. code-block:: python

    self.table.horizontal_header().section_resize_mode = QHeaderView.Stretch

Additionally, properties can also be declared directly in Shiboken for
non Qt-libraries, see :ref:`property-declare`.

More about features
-------------------

Detailed info about features can be found here: :ref:`feature-why`

Tools
-----

|project|  ships some Qt tools:

* ``pyside6-rcc``: Qt Resource Compiler. This is a command line tool
  that compiles ``.qrc`` files containing binary data, for example images,
  into executable Python code (see :ref:`using_qrc_files`).
* ``pyside6-uic``: Qt User Interface Compiler. This is a command line tool
  that compiles ``.ui`` files containing designs of Qt Widget-based forms
  into executable Python code (see :ref:`using_ui_files`).
* ``pyside6-assistant``: Qt Help Viewer. This is a graphical tool that can
  be used to view Qt documentation from Qt Compressed Help files (``.qhc``).
  Currently, only the binary without documentation sets is shipped to reduce the
  wheel size. For building the documentation, see :ref:`building_documentation`.
* ``pyside6-designer``: Qt User Interface Designer. This is a graphical tool
  to create designs of Qt Widget-based forms and use custom widgets
  (see :ref:`using_ui_files`, :ref:`designer_custom_widgets`).
