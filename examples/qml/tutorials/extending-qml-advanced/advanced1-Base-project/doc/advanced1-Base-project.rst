Extending QML (advanced) - BirthdayParty Base Project
=====================================================

This is the first of a series of 6 examples forming a tutorial using the
example of a birthday party to demonstrate some of the advanced features of
QML. The code for the various features explained below is based on this
birthday party project and relies on some of the material in the basic
tutorial. This simple example is then expanded upon to illustrate the various
QML extensions explained below. The complete code for each new extension to the
code can be found at the end of the respective page.

The base project defines the ``Person`` class and the ``BirthdayParty`` class,
which model the attendees and the party itself respectively.

.. literalinclude:: person.py
   :lineno-start: 13
   :lines: 13-41

.. literalinclude:: birthdayparty.py
   :lineno-start: 16
   :lines: 16-46

All the information about the party can then be stored in the corresponding QML
file.

.. literalinclude:: People/Main.qml
   :lineno-start: 4
   :lines: 4-16


The ``main.py`` file creates a simple shell application that displays whose
birthday it is and who is invited to their party.

.. literalinclude:: main.py
   :lineno-start: 17
   :lines: 17-21

The app outputs the following summary of the party::

    "Bob Jones" is having a birthday!
    They are inviting:
        "Leo Hodges"
        "Jack Smith"
        "Anne Brown"

Outlook
-------

The following sections go into how to add support for ``Boy`` and ``Girl``
attendees instead of just ``Person`` by using inheritance and coercion, how to
make use of default properties to implicitly assign attendees of the party as
guests, how to assign properties as groups instead of one by one, how to use
attached objects to keep track of invited guests' reponses, how to use a
property value source to display the lyrics of the happy birthday song over
time, and how to expose third party objects to QML.
