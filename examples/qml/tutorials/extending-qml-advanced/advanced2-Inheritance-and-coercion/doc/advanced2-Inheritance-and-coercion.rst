.. _qml-inheritance-and-coercion-example:

Extending QML - Inheritance and Coercion Example
================================================

This example builds on the :ref:`qml-adding-types-example` and the
:ref:`qml-object-and-list-property-types-example` .

The Inheritance and Coercion Example shows how to use base classes to assign
types of more than one type to a property.  It specializes the Person type
developed in the previous examples into two types - a ``Boy`` and a ``Girl``.

Declare Boy and Girl
--------------------

The Person class remains unaltered in this example and the Boy and Girl C++
classes are trivial extensions of it. The types and their QML name are
registered with the QML engine.

As an example, the inheritance used here is a little contrived, but in real
applications it is likely that the two extensions would add additional
properties or modify the Person classes behavior.

Running the Example
-------------------

The BirthdayParty type has not changed since the previous example. The
celebrant and guests property still use the People type.

However, as all three types, Person, Boy and Girl, have been registered with the
QML system, on assignment QML automatically (and type-safely) converts the Boy
and Girl objects into a Person.

The main.py file in the example includes a simple shell application that
loads and runs the QML snippet shown below.
