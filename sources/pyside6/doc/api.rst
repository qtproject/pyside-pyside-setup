.. _pyside-api:

Modules API
===========

Basic modules
-------------

These are the main modules that help you build a Widget-based UI.

.. grid:: 1 3 3 3
    :gutter: 2

    .. grid-item-card:: :mod:`Qt Core <PySide6.QtCore>`

        Core non-graphical classes used by other modules.

    .. grid-item-card:: :mod:`Qt GUI <PySide6.QtGui>`

        Base classes for graphical user interface (GUI) components.

    .. grid-item-card:: :mod:`Qt Widgets <PySide6.QtWidgets>`

        Classes to extend Qt GUI with Python widgets.

QML and Qt Quick
----------------

Use these modules to interact with the `QML Language <https://doc.qt.io/qt-6/qmlapplications.html>`_,
from Python.

.. grid:: 1 3 3 3
    :gutter: 2

    .. grid-item-card:: :mod:`Qt Qml <PySide6.QtQml>`

        Classes for QML and JavaScript languages.

    .. grid-item-card:: `Qt QML Core`_

        Provides core system functionality in QML, exposing platform‑independent
        application permissions and essential system‑related types.

    .. grid-item-card:: `Qt QML WorkerScript`_

        Enables the use of threads in a Qt Quick application.

    .. grid-item-card:: `Qt QML Models`_

        Contains types for defining data models in QML.

    .. grid-item-card:: :mod:`Qt Quick <PySide6.QtQuick>`

        A declarative framework for building highly dynamic applications
        with custom UIs.

    .. grid-item-card:: :mod:`Qt Quick Controls <PySide6.QtQuickControls2>`

        Lightweight QML types for creating performant user interfaces for
        desktop, embedded, and mobile devices.

    .. grid-item-card:: :mod:`Qt Quick Test <PySide6.QtQuickTest>`

        A unit test framework for QML applications, where the test cases
        are written as JavaScript functions.

    .. grid-item-card:: `Qt Quick Dialogs`_

        Types for creating and interacting with system dialogs from a Qt
        Quick application.

    .. grid-item-card:: `Qt Quick Layouts`_

        Layouts are items that are used to arrange Qt Quick 2 based items
        in the user interface.

    .. grid-item-card::  `Qt Labs StyleKit`_

        A dedicated styling API that streamlines styling Qt Quick Controls
        through a set of shared design attributes.

    .. grid-item-card:: :mod:`Qt Quick Widgets <PySide6.QtQuickWidgets>`

        Provides a Python widget class for displaying a Qt Quick user interface.


.. _`Qt QML Core`: https://doc.qt.io/qt-6/qtqmlcore-index.html
.. _`Qt QML WorkerScript`: https://doc.qt.io/qt-6/qmlworkerscript-index.html
.. _`Qt QML Models`: https://doc.qt.io/qt-6/qtqmlmodels-index.html
.. _`Qt Quick Dialogs`: https://doc.qt.io/qt-6/qtquickdialogs-index.html
.. _`Qt Quick Layouts`: https://doc.qt.io/qt-6/qtquicklayouts-index.html
.. _`Qt Labs StyleKit`: https://doc.qt.io/qt-6/qtlabsstylekit-index.html

All the modules
---------------

There are many other modules currently supported by |pymodname|, here you can find a complete list
of them.

.. toctree::

   modules.rst
