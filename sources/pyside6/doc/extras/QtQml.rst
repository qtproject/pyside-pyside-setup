The Qt QML module defines and implements the QML language

The Qt QML module provides a framework for developing applications and
libraries with the QML language. It defines and implements the language and
engine infrastructure, and provides an API to enable application developers to
extend the QML language with custom types and integrate QML code with
JavaScript and C++. The Qt QML module provides both a `QML API
<https://doc.qt.io/qt-6/qtqml-qmlmodule.html>`_ and a `C++ API
<https://doc.qt.io/qt-6/qtqml-module.html>`_ .

Note that while the Qt QML module provides the language and infrastructure for
QML applications, the :ref:`Qt Quick<Qt-Quick>` module provides many visual
components, model-view support, an animation framework, and much more for
building user interfaces.

For those new to QML and Qt Quick, please see QML Applications for an
introduction to writing QML applications.

Using the Module
^^^^^^^^^^^^^^^^

To include the definitions of modules classes, use the following
directive:

::

    import PySide6.QtQml

The module also provides `QML types <http://doc.qt.io/qt-6/qtqml-qmlmodule.html>`_ .

QML and QML Types
^^^^^^^^^^^^^^^^^

The Qt QML module contains the QML framework and important QML types used in
applications. The constructs of QML are described in the
:ref:`The QML Reference<The-QML-Reference>` .

In addition to the :ref:`QML Basic Types<QML-Basic-Types>` , the module comes
with the following QML object types:

    * `Component <https://doc.qt.io/qt-6/qml-qtqml-component.html>`_
    * `QtObject <https://doc.qt.io/qt-6/qml-qtqml-qtobject.html>`_
    * `Binding <https://doc.qt.io/qt-6/qml-qtqml-binding.html>`_
    * `Connections <https://doc.qt.io/qt-6/qml-qtqml-connections.html>`_
    * `Timer <https://doc.qt.io/qt-6/qml-qtqml-timer.html>`_

The `Qt <https://doc.qt.io/qt-6/qml-qtqml-qt.html>`_ global object provides
useful enums and functions for various QML types.

Lists and Models
^^^^^^^^^^^^^^^^

New in Qt 5.1, the model types are moved to a submodule, ``QtQml.Models``\. The
Qt QML Models page has more information.

    * DelegateModel
    * DelegateModelGroup
    * ListElement
    * ListModel
    * ObjectModel

JavaScript Environment for QML Applications
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

JavaScript expressions allow QML code to contain application logic. Qt QML
provides the framework for running JavaScript expressions in QML and from C++.

These sections are from :ref:`The QML Reference<The-QML-Reference>` .

    * `Integrating QML and JavaScript <https://doc.qt.io/qt-6/qtqml-javascript-topic.html>`_
    * `Using JavaScript Expressions with QML <https://doc.qt.io/qt-6/qtqml-javascript-expressions.html>`_
    * `Dynamic QML Object Creation from JavaScript <https://doc.qt.io/qt-6/qtqml-javascript-dynamicobjectcreation.html>`_
    * `Defining JavaScript Resources In QML <https://doc.qt.io/qt-6/qtqml-javascript-resources.html>`_
    * `Importing JavaScript Resources In QML <https://doc.qt.io/qt-6/qtqml-javascript-imports.html>`_
    * `JavaScript Host Environment <https://doc.qt.io/qt-6/qtqml-javascript-hostenvironment.html>`_
