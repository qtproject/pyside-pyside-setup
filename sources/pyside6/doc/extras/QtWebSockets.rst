Provides an implementation of the WebSocket protocol.

WebSocket is a web-based protocol designed to enable two-way communication
between a client application and a remote host. It enables the two entities to
send data back and forth if the initial handshake succeeds. WebSocket is the
solution for applications that struggle to get real-time data feeds with less
network latency and minimum data exchange.

The Qt WebSockets module provides C++ and QML interfaces that enable Qt
applications to act as a server that can process WebSocket requests, or a
client that can consume data received from the server, or both.

Getting Started
^^^^^^^^^^^^^^^

To include the definitions of modules classes, use the following
directive:

::

    import PySide6.QtWebSockets

The module also provides `QML types <http://doc.qt.io/qt-6/qtwebsockets-qmlmodule.html>`_ .

Articles and Guides
^^^^^^^^^^^^^^^^^^^

    * `Overview <https://doc.qt.io/qt-6/websockets-overview.html>`_
    * `Testing Qt WebSockets <https://doc.qt.io/qt-6/qtwebsockets-testing.html>`_
