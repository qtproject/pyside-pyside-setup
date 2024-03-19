.. _pyside6-qmlcachegen:

pyside6-qmlcachegen
===================

``pyside6-qmlcachegen`` is a command line tool that wraps `qmlcachegen`_.
This tool creates C++ code or `QML byte code` for ``.qml`` files. For
Qt for Python, only `QML byte code` is relevant. The file suffix is
``.qmlc`` and it works similar to compiled Python bytecode
(``.pyc`` files).

Usage
-----

The command line option ``--only-bytecode`` should be used to
create `QML byte code`. For example:

.. code-block:: bash

    qmlcachegen --only-bytecode gallery.qml

produces a file ``gallery.qmlc`` containing `QML byte code` which is
automatically loaded by the QML engine.

.. _`qmlcachegen`: https://doc.qt.io/qt-6/qtqml-tool-qmlcachegen.html
