 Qt Quick Test is a unit test framework for QML applications. Test cases are
 written as JavaScript functions within a QML TestCase type:

.. code-block:: JavaScript

    import QtQuick
    import QtTest

    TestCase {
        name: "MathTests"

        function test_math() {
            compare(2 + 2, 4, "2 + 2 = 4")
        }

        function test_fail() {
            compare(2 + 2, 5, "2 + 2 = 5")
        }
    }

Functions whose names start with ``test_`` are treated as test cases to be
executed.

QML API
^^^^^^^

The `QML types <https://doc.qt.io/qt-6/qttest-qmlmodule.html>`_
in Qt Quick Test are available through the ``QtTest`` import.
To use the types, add the following import statement to your ``.qml`` file:

.. code-block:: JavaScript

    import QtTest

Running Tests
^^^^^^^^^^^^^

Test cases are launched by a harness that consists of the following code:

.. code-block:: Python

    import sys
    from PySide6.QtQuickTest import QUICK_TEST_MAIN

    QUICK_TEST_MAIN("example", sys.argv)

Where "example" is the identifier to use to uniquely identify this set of
tests.

Test execution can be controlled by a number of command line options (pass
``-h`` for help).

Executing Code Before QML Tests
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To execute code before any of the QML tests are run, the
:py:func:`QUICK_TEST_MAIN_WITH_SETUP` function can be used. This can be useful
for setting context properties on the QML engine, amongst other things.
