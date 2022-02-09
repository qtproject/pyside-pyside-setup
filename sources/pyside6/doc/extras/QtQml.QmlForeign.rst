.. currentmodule:: PySide6.QtQml
.. _QmlForeign:

QmlForeign
**********

.. py:decorator:: QmlForeign

   This decorator can be used to change the type that is created by QML.

   This is useful for registering types that cannot be amended by adding the
   QmlElement decorator, for example because they belong to 3rdparty libraries.

   .. code-block:: python

      QML_IMPORT_NAME = "com.library.name"
      QML_IMPORT_MAJOR_VERSION = 1
      QML_IMPORT_MINOR_VERSION = 0 # Optional

      @QmlNamedElement("QWidget")
      @QmlForeign(QWidget)
      class ForeignWidgetHelperClass(QObject):
          ...

   Afterwards the class may be used in QML:

   .. code-block:: javascript

      import com.library.name 1.0

      QWidget {
         // ...
      }
