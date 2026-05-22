The Qt Qml module implements the QML language and offers APIs to register types
for it.

The Qt Qml module provides a framework for developing applications and
libraries with the :ref:`QML language <The-QML-Reference>` .
It defines and implements the language and engine infrastructure, and
provides an API to enable application developers to :ref:`Qt-Qml`
custom QML types and modules and integrate QML code with JavaScript and
Python. The Qt Qml module provides both a `QML API`_ and a Python API.

Using the Module
^^^^^^^^^^^^^^^^

To include the definitions of modules classes, use the following
directive:

::

    import PySide6.QtQml

Registering QML Types and QML Modules
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

See :ref:`tutorial_qmlintegration`.

Tweaking the engine
^^^^^^^^^^^^^^^^^^^

There are a number of knobs you can turn to customize the behavior of the QML
engine. The page on :ref:`Configuring-the-JavaScript-Engine` lists the
environment variables you may use to this effect. The description of the
:ref:`The-QML-Disk-Cache` describes the options related to how your QML
components are compiled and loaded.

Articles and Guides
^^^^^^^^^^^^^^^^^^^

These articles contain information about Qt Qml.

* :ref:`The-QML-Reference`
* `Qt Qml Tooling`_
* :ref:`tutorial_qmlintegration`
* :ref:`Singletons-in-QML`

.. _`QML API`: https://doc.qt.io/qt-6/qtqml-qmlmodule.html
.. _`Qt Qml Tooling`: https://doc.qt.io/qt-6/qtqml-tooling.html
