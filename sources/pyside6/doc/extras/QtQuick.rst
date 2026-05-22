The Qt Quick module implements the "standard library" for QML

The Qt Quick module is the standard library for writing QML applications. While
the :mod:`PySide6.QtQml` module provides the QML engine and language
infrastructure, the Qt Quick module provides all the basic types necessary for
creating user interfaces with QML. It provides a visual canvas and includes
types for creating and animating visual components, receiving user input,
creating data models and views and delayed object instantiation.

The Qt Quick module provides both a `QML API`_ , which supplies QML types
for creating user interfaces with the QML language, and a Python for extending
QML applications with Python code.

.. note:: A set of Qt Quick-based UI controls is also available to create user
          interfaces. See :mod:`PySide6.QtQuickControls2` for more information.

If you're new to QML and Qt Quick, please see
:ref:`Getting-started-with-Qt-Quick-applications` for an introduction
to writing QML applications.

Using the Module
^^^^^^^^^^^^^^^^

To include the definitions of modules classes, use the following
directive:

::

    import PySide6.QtQuick

Important Concepts in Qt Quick
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Qt Quick provides everything you need to create a rich application with a fluid
and dynamic user interface. It enables you to build user interfaces around the
behavior of user interface components and how they connect with one another,
and it provides a visual canvas with its own coordinate system and rendering
engine. Animation and transition effects are first class concepts in Qt Quick,
and you can add visual effects through specialized components for particle and
shader effects.

* :ref:`Important-Concepts-In-Qt-Quick---The-Visual-Canvas`
* :ref:`Important-Concepts-In-Qt-Quick---User-Input`
* :ref:`Important-Concepts-In-Qt-Quick---Positioning`
* :ref:`Important-Concepts-in-Qt-Quick---States--Transitions-and-Animations`
* :ref:`Important-Concepts-In-Qt-Quick---Data---Models--Views--and-Data-Storage`
* :ref:`Important-Concepts-In-Qt-Quick---Graphical-Effects`
* :ref:`Important-Concepts-In-Qt-Quick---Convenience-Types`

When using the Qt Quick module, you will need to know how to write QML
applications using the QML language. In particular, QML Basics and QML
Essentials from the :ref:`Getting-started-with-Qt-Quick-applications` page.

To find out more about using the QML language, see the
:mod:`PySide6.QtQml` module documentation.

Extension Points
^^^^^^^^^^^^^^^^

* :ref:`C---Extension-Points-Provided-By-Qt-Quick`

Articles and Guides
^^^^^^^^^^^^^^^^^^^

* :ref:`Best-Practices-for-QML-and-Qt-Quick`
* :ref:`Qt-Quick-Tools-and-Utilities`

Further information for writing QML applications:

* :ref:`Getting-started-with-Qt-Quick-applications` - essential information for application development with QML and Qt Quick
* :mod:`PySide6.QtQml` - documentation for the Qt Qml module, which provides the QML engine and language infrastructure
* :ref:`Qt-Quick-How-tos` - shows how to achieve specific tasks in Qt Quick

Qt Academy Courses
^^^^^^^^^^^^^^^^^^

* `Introduction to Qt Quick`_

.. _`QML API`: https://doc.qt.io/qt-6/qtquick-qmlmodule.html
.. _`Introduction to Qt Quick`: https://www.qt.io/academy/course-catalog#introduction-to-qt-quick
