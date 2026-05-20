The Qt Test module provides auxiliary API for testing Qt applications.
The :class:`~PySide6.QtTest.QSignalSpy` class provides easy
introspection for Qt's signals and slots, and the
:class:`~PySide6.QtTest.QAbstractItemModelTester` allows for non-destructive
testing of item models.

.. note:: Not all macros in the `C++ version of QtTest`_ were exposed in PySide.
          This module is useful only for GUI testing and benchmarking; for ordinary unit
          testing you should use the `pytest`_ Python module.

.. _`pytest`: https://docs.pytest.org/en/stable
.. _`C++ version of QtTest`: https://doc.qt.io/qt-6/qttest-index.html

Using the Module
^^^^^^^^^^^^^^^^

To include the definitions of the module's classes, use the following directive:

::

    import PySide6.QtTest
