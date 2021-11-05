.. _qml-default-property-example:

Extending QML - Default Property Example
========================================

This example builds on the :ref:`qml-adding-types-example`,
the :ref:`qml-object-and-list-property-types-example` and
the :ref:`qml-inheritance-and-coercion-example`.

The Default Property Example is a minor modification of the
:ref:`qml-inheritance-and-coercion-example` that simplifies the
specification of a BirthdayParty through the use of a default property.

Declaring the BirthdayParty Class
---------------------------------

The only difference between this example and the last, is the addition of a
``DefaultProperty`` class info annotation.

The default property specifies the property to assign to whenever an explicit
property is not specified, in the case of the BirthdayParty type the guest
property.  It is purely a syntactic simplification, the behavior is identical
to specifying the property by name, but it can add a more natural feel in many
situations.  The default property must be either an object or list property.

Running the Example
-------------------

The main.py file in the example includes a simple shell application that
loads and runs the QML snippet shown below.
