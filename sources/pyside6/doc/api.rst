.. _pyside-api:

Modules API
===========

Basic modules
-------------

These are the main modules that help you build a Widget-based UI.

.. grid:: 1 3 3 3
    :gutter: 2

    .. grid-item-card:: :mod:`QtCore <PySide6.QtCore>`

        Provides core non-GUI functionality, like signal and slots, properties,
        base classes of item models, serialization, and more.

    .. grid-item-card:: :mod:`QtGui <PySide6.QtGui>`

        Extends QtCore with GUI functionality: Events, windows and screens,
        OpenGL and raster-based 2D painting, as well as images.

    .. grid-item-card:: :mod:`QtWidgets <PySide6.QtWidgets>`

        Provides ready to use Widgets for your application, including graphical
        elements for your UI.

QML and Qt Quick
----------------

Use these modules to interact with the `QML Language <https://doc.qt.io/qt-5.qmlapplications>`_,
from Python.

.. grid:: 1 3 3 3
    :gutter: 2

    .. grid-item-card:: :mod:`QtQml <PySide6.QtQml>`

        The base Python API to interact with the module.

    .. grid-item-card:: :mod:`QtQuick <PySide6.QtQuick>`

        Provides classes to embed Qt Quick in Qt applications.

    .. grid-item-card:: :mod:`QtQuickWidgets <PySide6.QtQuickWidgets>`

        Provides the QQuickWidget class to embed Qt Quick in widget-based
        applications.

All the modules
---------------

There are many other modules currently supported by |pymodname|, here you can find a complete list
of them.

.. toctree::

   modules.rst
