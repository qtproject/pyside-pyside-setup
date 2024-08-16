Extending QML - Object and List Property Types Example
======================================================

Exporting C++ Properties.

This example builds on :ref:`example_qml_tutorials_extending-qml-advanced_adding`.

The Object and List Property Types example shows how to add object and list
properties in QML. This example adds a BirthdayParty type that specifies a
birthday party, consisting of a celebrant and a list of guests. People are
specified using the People QML type built in the previous example.

import examples.properties.people

.. code-block:: javascript

    BirthdayParty {
        host: Person {
            name: "Bob Jones"
            shoe_size: 12
        }
        guests: [
            Person { name: "Leo Hodges" },
            Person { name: "Jack Smith" },
            Person { name: "Anne Brown" }
        ]
    }

Declare the BirthdayParty
-------------------------

The BirthdayParty class is declared like this:

.. code-block:: python

    from person import Person


    # To be used on the @QmlElement decorator
    # (QML_IMPORT_MINOR_VERSION is optional)
    QML_IMPORT_NAME = "People"
    QML_IMPORT_MAJOR_VERSION = 1


    @QmlElement
    class BirthdayParty(QObject):

        def __init__(self, parent=None):
            super().__init__(parent)
            self._host = None
            self._guests = []

        @Property(Person)
        def host(self):
            return self._host

        @host.setter
        def host(self, h):
            self._host = h

        def guest(self, n):
            return self._guests[n]

        def guestCount(self):
            return len(self._guests)

        def appendGuest(self, guest):
            self._guests.append(guest)

        guests = ListProperty(Person, appendGuest)

The class contains a member to store the celebrant object, and also a
list member storing the Person instances.

In QML, the type of a list properties - and the guests property is a list of
people - are all of type :class:`~PySide6.QtQml.ListProperty`.
``ListProperty`` is a simple value type that contains a set of functions.
QML calls these functions whenever it needs to read from, write to or otherwise
interact with the list. In addition to concrete lists like the people list used in this
example, the use of ``ListProperty`` allows for "virtual lists" and other advanced
scenarios.

Running the Example
-------------------

The main.py file in the example includes a simple shell application that
loads and runs the QML snippet shown at the beginning of this page.
