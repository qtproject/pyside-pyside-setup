Bridges the gap between Qt applications and HTML/JavaScript.

Qt WebChannel enables peer-to-peer communication between a server (QML/Python
application) and a client (HTML/JavaScript or QML application). It is supported
out of the box by :ref:`Qt WebEngine<Qt-WebEngine>` . In addition it can work
on all browsers that support :ref:`WebSockets<Qt-WebSockets>` , enabling Qt
WebChannel clients to run in any JavaScript environment (including QML). This
requires the implementation of a custom transport based on Qt WebSockets.

The module provides a JavaScript library for seamless integration of Python and
QML applications with HTML/JavaScript and QML clients. The clients must use the
JavaScript library to access the serialized QObjects published by the host
applications.

Getting Started
^^^^^^^^^^^^^^^

To include the definitions of modules classes, use the following
directive:

::

    import PySide6.QtWebChannel

API Reference
^^^^^^^^^^^^^

    * `JavaScript API <https://doc.qt.io/qt-6/qtwebchannel-javascript.html>`_

The module also provides `QML types <https://doc.qt.io/qt-6/qtwebchannel-qmlmodule.html>`_ .
