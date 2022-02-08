.. currentmodule:: PySide6.QtQml
.. _QmlExtended:

QmlExtended
***********

.. py:decorator:: QmlExtended

Declares that the enclosing type uses the type passed as an extension to
provide further properties, methods, and enumerations in QML. This takes effect
if the type is exposed to QML using a ``QmlElement()`` or ``QmlNamedElement()``
decorator.

.. code-block:: python

    QML_IMPORT_NAME = "com.library.name"
    QML_IMPORT_MAJOR_VERSION = 1
    QML_IMPORT_MINOR_VERSION = 0 # Optional

    class LineEditExtension(QObject):
        pass

    @QmlNamedElement("QLineEdit")
    @QmlExtended(LineEditExtension)
    @QmlForeign(QLineEdit)
    class LineEditForeign(QObject):
        ...

Afterwards the class may be used in QML:

.. code-block:: javascript

      import com.library.name 1.0

      QLineEdit {
          left_margin: 10
      }
