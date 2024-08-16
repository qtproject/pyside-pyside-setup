Extending QML (advanced) - Property Value Source
================================================

This is the last of a series of 6 examples forming a tutorial using the example
of a birthday party to demonstrate some of the advanced features of QML.

During the party the guests have to sing for the host. It would be handy if the
program could display the lyrics customized for the occasion to help the
guests. To this end, a property value source is used to generate the verses of
the song over time.

.. literalinclude:: happybirthdaysong.py
    :lineno-start: 13
    :lines: 13-49

The class ``HappyBirthdaySong`` is added as a value source. It must inherit
from ``QQmlPropertyValueSource`` and implement its interface. The
``setTarget()`` function is used to define which property this source acts
upon. In this case, the value source writes to the ``announcement`` property of
the ``BirthdayParty`` to display the lyrics over time. It has an internal timer
that causes the ``announcement`` property of the party to be set to the next
line of the lyrics repeatedly.

In QML, a ``HappyBirthdaySong`` is instantiated inside the ``BirthdayParty``.
The ``on`` keyword in its signature is used to specify the property that the
value source targets, in this case ``announcement``. The ``name`` property of
the ``HappyBirthdaySong`` object is also bound to the name of the host of the
party.

.. literalinclude:: People/Main.qml
    :lineno-start: 6
    :lines: 6-7

The program displays the time at which the party started using the
``partyStarted`` signal and then prints the following happy birthday verses
over and over::

    Happy birthday to you,
    Happy birthday to you,
    Happy birthday dear Bob Jones,
    Happy birthday to you!
