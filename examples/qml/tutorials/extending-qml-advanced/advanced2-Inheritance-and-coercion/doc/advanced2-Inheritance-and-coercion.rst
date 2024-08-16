Extending QML (advanced) - Inheritance and Coercion
===================================================

This is the second of a series of 6 examples forming a tutorial using the
example of a birthday party to demonstrate some of the advanced features of
QML.

Right now, each attendant is being modelled as a person. This is a bit too
generic and it would be nice to be able to know more about the attendees. By
specializing them as boys and girls, we can already get a better idea of who's
coming.

To do this, the ``Boy`` and ``Girl`` classes are introduced, both inheriting from
``Person``.

.. literalinclude:: person.py
    :lineno-start: 43
    :lines: 43-46

.. literalinclude:: person.py
    :lineno-start: 49
    :lines: 49-52

The ``Person`` class remains unaltered and the ``Boy`` and ``Girl`` classes are
trivial extensions of it. The types and their QML name are registered with the
QML engine with ``@QmlElement``.

Notice that the ``host`` and ``guests`` properties in ``BirthdayParty`` still
take instances of ``Person``.

.. literalinclude:: birthdayparty.py
    :lineno-start: 26
    :lines: 26-26

.. literalinclude:: birthdayparty.py
    :lineno-start: 46
    :lines: 46-46

The implementation of the ``Person`` class itself has not been changed.
However, as the ``Person`` class was repurposed as a common base for ``Boy``
and ``Girl``, ``Person`` should no longer be instantiable from QML directly. An
explicit ``Boy`` or ``Girl`` should be instantiated instead.

.. literalinclude:: person.py
    :lineno-start: 13
    :lines: 13-15

While we want to disallow instantiating ``Person`` from within QML, it still
needs to be registered with the QML engine so that it can be used as a property
type and other types can be coerced to it. This is what the ``@QmlUncreatable``
macro does. As all three types, ``Person``, ``Boy`` and ``Girl``, have been
registered with the QML system, on assignment, QML automatically (and
type-safely) converts the ``Boy`` and ``Girl`` objects into a ``Person``.

With these changes in place, we can now specify the birthday party with the
extra information about the attendees as follows.

.. literalinclude:: People/Main.qml
    :lineno-start: 6
    :lines: 6-16
