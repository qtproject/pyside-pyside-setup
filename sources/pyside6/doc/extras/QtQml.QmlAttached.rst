.. currentmodule:: PySide6.QtQml
.. _QmlAttached:

QmlAttached
***********

.. py:decorator:: QmlAttached

This decorator declares that the enclosing type attaches the type passed as
an attached property to other types. This takes effect if the type is exposed
to QML using a ``QmlElement()`` or ``@QmlNamedElement()`` decorator.

.. code-block:: python

    QML_IMPORT_NAME = "com.library.name"
    QML_IMPORT_MAJOR_VERSION = 1
    QML_IMPORT_MINOR_VERSION = 0 # Optional

    @QmlAnonymous
    class LayoutAttached(QObject):
        @Property(QMargins)
        def margins(self):
           ...

    @QmlElement()
    @QmlAttached(LayoutAttached)
    class Layout(QObject):
          ...

Afterwards the class may be used in QML:

.. code-block:: javascript

      import com.library.name 1.0

      Layout {
         Widget {
             Layout.margins: [2, 2, 2, 2]
         }
      }
