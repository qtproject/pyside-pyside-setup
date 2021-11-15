.. currentmodule:: PySide6.QtQml
.. _QmlSingleton:

QmlSingleton
************

.. py:decorator:: QmlSingleton

Declares the decorated type to be a singleton in QML. This only takes effect if
the type is a Q_OBJECT and is available in QML (by having a QmlElement decorator).
The QQmlEngine will try to create a singleton instance using the type's default
constructor.

.. code-block:: python

    QML_IMPORT_NAME = "com.library.name"
    QML_IMPORT_MAJOR_VERSION = 1
    QML_IMPORT_MINOR_VERSION = 0 # Optional

    @QmlElement
    @QmlSingleton
    class ClassForQml(QObject):
        # ...

.. note:: The order of the decorators matters; ``QmlSingleton`` needs to be preceded by ``QmlElement``.
