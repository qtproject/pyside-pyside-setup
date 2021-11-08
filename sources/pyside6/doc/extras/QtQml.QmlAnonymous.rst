.. currentmodule:: PySide6.QtQml
.. _QmlAnonymous:

QmlAnonymous
************

.. py:decorator:: QmlAnonymous

   Declares the enclosing type to be available, but anonymous in QML. The type
   cannot be created or used to declare properties in QML, but when passed from
   C++, it is recognized. In QML, you can use properties of this type if they
   are declared in C++.

   .. code-block:: python

      QML_IMPORT_NAME = "com.library.name"
      QML_IMPORT_MAJOR_VERSION = 1
      QML_IMPORT_MINOR_VERSION = 0 # Optional

      @QmlAnonymous
      class ClassForQml(QObject):
          # ...
