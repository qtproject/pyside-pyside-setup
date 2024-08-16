Extending QML (advanced) - Default Properties
=============================================

This is the third of a series of 6 examples forming a tutorial using the
example of a birthday party to demonstrate some of the advanced features of
QML.

Currently, in the QML file, each property is assigned explicitly. For example,
the ``host`` property is assigned a ``Boy`` and the ``guests`` property is
assigned a list of ``Boy`` or ``Girl``. This is easy but it can be made a bit
simpler for this specific use case. Instead of assigning the ``guests``
property explicitly, we can add ``Boy`` and ``Girl`` objects inside the party
directly and have them assigned to ``guests`` implicitly. It makes sense that
all the attendees that we specify, and that are not the host, are guests. This
change is purely syntactical but it can add a more natural feel in many
situations.

The ``guests`` property can be designated as the default property of
``BirthdayParty``. Meaning that each object created inside of a
``BirthdayParty`` is implicitly appended to the default property ``guests``.
The resulting QML looks like this.

.. literalinclude:: People/Main.qml
    :lineno-start: 6
    :lines: 6-15

The only change required to enable this behavior is to add the ``DefaultProperty``
class info annotation to ``BirthdayParty`` to designate ``guests`` as its default
property.

.. literalinclude:: birthdayparty.py
    :lineno-start: 16
    :lines: 16-18

You may already be familiar with this mechanism. The default property for all
descendants of ``Item`` in QML is the ``data`` property. All elements not
explicitly added to a property of an ``Item`` will be added to ``data``. This
makes the structure clear and reduces unnecessary noise in the code.
