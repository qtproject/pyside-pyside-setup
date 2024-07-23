
Qt WebView lets you display web content inside a QML application. To avoid including a full web
browser stack, Qt WebView uses native APIs where appropriate.

Getting Started
^^^^^^^^^^^^^^^

To include the definitions of modules classes, use the following
directive:

    ::

        from PySide6.QtWebView import QtWebView

To make the Qt WebView module function correctly across all platforms, it's
necessary to call ``QtWebView.initialize()`` before creating the QGuiApplication
instance and before window's QPlatformOpenGLContext is created. For usage,
see the ``minibrowser`` example in the PySide6 examples package.

API Reference
^^^^^^^^^^^^^

    * `Qt API <https://doc.qt.io/qt-6/qtwebview-index.html>`_

The module also provides `QML types <https://doc.qt.io/qt-6/qtwebview-index.html#qml-api>`_
