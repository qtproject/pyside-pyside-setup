.. _tutorial_qml_debugging:

Mixed mode Debugging of PySide6 QML Applications
************************************************

Using Qt Creator's QML Debugger for a PySide6 QML Application
=============================================================

Besides the C++ debugger, *Qt Creator* provides a `QML debugger`_ which lets you
inspect JavaScript code. It works by connecting to a socket server run by the
``QmlEngine`` instance. The port is passed on the command line. To enable it,
add the below code to your QML application:

.. code-block:: python

        from argparse import ArgumentParser, RawTextHelpFormatter

        ...

        if __name__ == "__main__":
            argument_parser = ArgumentParser(...)
            argument_parser.add_argument("-qmljsdebugger", action="store",
                                         help="Enable QML debugging")
            options = argument_parser.parse_args()
            if options.qmljsdebugger:
                QQmlDebuggingEnabler.enableDebugging(True)
            app = QApplication(sys.argv)


For instructions on how to use the QML debugger, see
`Debugging a Qt Quick Example Application`_.

.. note:: The code should be removed or disabled when shipping the application
          as it poses a security risk.

Using the Qt Python VSCode Extension
====================================

The `Qt Python extension`_ for Visual Studio Code provides an easier way to debug
PySide6 QML applications with mixed-mode debugging support for both Python and QML.
The extension comes with several preset launch configurations that enable seamless
debugging without manual setup:

- ``Qt: PySide: Launch`` - Launch and debug PySide6 applications
- ``Qt: PySide: Launch with QML debugger`` - Launch PySide6 applications with QML debugging enabled
- ``Qt: QML: Attach by port`` - Attach the QML debugger to a running application by port number

With these configurations, you can set breakpoints in both your Python code and QML
files, inspect variables, and step through code execution across the Python-QML boundary.
For mixed Python and QML debugging, you can use a compound configuration that combines
``Qt: PySide: Launch with QML debugger`` and ``Qt: QML: Attach by port`` to debug both
layers simultaneously.

For detailed instructions on how to debug PySide6 applications using the Qt Python
extension, see `Debugging Qt for Python Applications in VSCode`_.

.. _`QML debugger`: https://doc.qt.io/qtcreator/creator-debugging-qml.html
.. _`Debugging a Qt Quick Example Application`: https://doc.qt.io/qtcreator/creator-qml-debugging-example.html
.. _`Qt Python extension`: https://marketplace.visualstudio.com/items?itemName=TheQtCompany.qt-python
.. _`Debugging Qt for Python Applications in VSCode`: https://doc-snapshots.qt.io/vscodeext-dev/vscodeext-how-debug-apps-python.html
