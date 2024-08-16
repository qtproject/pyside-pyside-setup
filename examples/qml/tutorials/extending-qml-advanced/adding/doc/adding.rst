Extending QML - Adding Types Example
====================================

The Adding Types Example shows how to add a new object type, ``Person``, to QML.
The ``Person`` type can be used from QML like this:

.. code-block:: javascript

    import examples.adding.people

    Person {
        name: "Bob Jones"
        shoe_size: 12
    }

Declare the Person Class
------------------------

All QML types map to C++ types. Here we declare a basic C++ Person class
with the two properties we want accessible on the QML type - name and shoeSize.
Although in this example we use the same name for the C++ class as the QML
type, the C++ class can be named differently, or appear in a namespace.

The Person class implementation is quite basic. The property accessors simply
return members of the object instance.

.. code-block:: python

    from PySide6.QtCore import QObject, Property
    from PySide6.QtQml import QmlElement

    # To be used on the @QmlElement decorator
    # (QML_IMPORT_MINOR_VERSION is optional)
    QML_IMPORT_NAME = "People"
    QML_IMPORT_MAJOR_VERSION = 1


    @QmlElement
    class Person(QObject):
        def __init__(self, parent=None):
            super().__init__(parent)
            self._name = ''
            self._shoe_size = 0

        @Property(str)
        def name(self):
            return self._name

        @name.setter
        def name(self, n):
            self._name = n

        @Property(int)
        def shoe_size(self):
            return self._shoe_size

        @shoe_size.setter
        def shoe_size(self, s):
            self._shoe_size = s

Running the Example
-------------------

The main.py file in the example includes a simple shell application that
loads and runs the QML snippet shown at the beginning of this page.
