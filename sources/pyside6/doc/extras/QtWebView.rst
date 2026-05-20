A light-weight web view.

Qt WebView lets you display web content inside a QML application. To avoid
including a full web browser stack, Qt WebView uses native APIs where
appropriate.

This is useful on mobile platforms, such as Android and iOS. On iOS, policies
dictate that all web content is displayed using the operating system's web
view.

On Windows, Qt WebView can use both :ref:`Qt-WebEngine` module and `WebView2`_
to render content.

On Linux, Qt WebView depends on the :ref:`Qt-WebEngine` module to render content.

On macOS, the system web view is used in the same manner as iOS.

.. _`WebView2`: https://learn.microsoft.com/en-us/microsoft-edge/webview2

Prerequisites
^^^^^^^^^^^^^

To make the Qt WebView module function correctly across all platforms, it's
necessary to call :meth:`~PySide6.QtWebView.QtWebView.initialize` before
creating the :class:`~PySide6.QtGui.QGuiApplication` instance and before
window's ``QPlatformOpenGLContext`` is created.

Limitations
^^^^^^^^^^^

Due to platform limitations, overlapping the Qt WebView with other QML
components is not supported. Doing this will have unpredictable results, which
may differ from platform to platform. Applications can also not rely on events
in the Qt WebView to propagate into the Qt event delivery system. E.g. it is
not possible to "overlay" an invisible item on top of the WebView to handle
certain events, or to handle events that the Qt WebView doesn't process in a
parent item.
