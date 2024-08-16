Extending QML (advanced) - Attached Properties
==============================================

This is the fifth of a series of 6 examples forming a tutorial using the
example of a birthday party to demonstrate some of the advanced features of
QML.

The time has come for the host to send out invitations. To keep track of which
guests have responded to the invitation and when, we need somewhere to store
that information. Storing it in the ``BirthdayParty`` object iself would not
really fit. A better way would be to store the responses as attached objects to
the party object.

First, we declare the ``BirthdayPartyAttached`` class which holds the guest reponses.

.. literalinclude:: birthdayparty.py
    :lineno-start: 16
    :lines: 16-32

And we attach it to the ``BirthdayParty`` class and define
``qmlAttachedProperties()`` to return the attached object.

.. literalinclude:: birthdayparty.py
    :lineno-start: 34
    :lines: 34-38

.. literalinclude:: birthdayparty.py
    :lineno-start: 67
    :lines: 67-69

Now, attached objects can be used in the QML to hold the rsvp information of
the invited guests.

.. literalinclude:: People/Main.qml
    :lineno-start: 6
    :lines: 6-22

Finally, the information can be accessed in the following way.

.. literalinclude:: main.py
    :lineno-start: 36
    :lines: 36-39

The program outputs the following summary of the party to come::

    "Jack Smith" is having a birthday!
    He is inviting:
        "Robert Campbell" RSVP date: "Wed Mar 1 2023"
        "Leo Hodges" RSVP date: "Mon Mar 6 2023"
