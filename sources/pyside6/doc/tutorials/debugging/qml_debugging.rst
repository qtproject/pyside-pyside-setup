Using Qt Creator's QML Debugger for a PySide6 QML Application
*************************************************************

Besides the C++ debugger, Qt Creator provides a `QML debugger`_ which lets you
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

.. _`QML debugger`: https://doc.qt.io/qtcreator/creator-debugging-qml.html
.. _`Debugging a Qt Quick Example Application`: https://doc.qt.io/qtcreator/creator-qml-debugging-example.html
