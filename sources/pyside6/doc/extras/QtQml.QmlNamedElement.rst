.. currentmodule:: PySide6.QtQml
.. _QmlNamedElement:

QmlNamedElement
***************

.. py:decorator:: QmlNamedElement

   This decorator registers a class it is attached to for use in QML under
   a name different from the class name, using global variables to specify
   the import name and version.

   .. code-block:: python

      QML_IMPORT_NAME = "com.library.name"
      QML_IMPORT_MAJOR_VERSION = 1
      QML_IMPORT_MINOR_VERSION = 0 # Optional

      @QmlNamedElement("ClassForQml")
      class ClassWithSomeName(QObject):
          ...

   Afterwards the class may be used in QML:

   .. code-block:: javascript

      import com.library.name 1.0

      ClassForQml {
         // ...
      }
