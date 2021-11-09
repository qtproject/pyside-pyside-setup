.. currentmodule:: PySide6.QtQml
.. _QmlUncreatable:

QmlUncreatable
**************

.. py:decorator:: QmlUncreatable

Declares that the decorated type shall not be creatable from QML. This takes
effect if the type is available in QML, by a preceding ``QmlElement``
decorator. The reason will be emitted as error message if an attempt to create
the type from QML is detected.

Some QML types are implicitly uncreatable, in particular types exposed with
``QmlAnonymous``.

Passing None or no argument will cause a standard message to be used instead.

.. code-block:: python
   QML_IMPORT_NAME = "com.library.name"
   QML_IMPORT_MAJOR_VERSION = 1
   QML_IMPORT_MINOR_VERSION = 0 # Optional


   @QmlElement
   @QmlUncreatable("BaseClassForQml is an abstract base class")
   class BaseClassForQml(QObject):
       # ...

.. note:: The order of the decorators matters, ``QmlUncreatable`` needs to be preceded by ``QmlElement``.
