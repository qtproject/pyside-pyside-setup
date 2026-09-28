.. _typediscovery:

**************
Type Discovery
**************

When converting objects which are part of a class hierarchy from a pointer to a
base class, it is expected to get the Python type of the actual, most derived
type, as opposed to C++ which requires a cast for this:

.. code-block:: python

    def event(self, event):
        if event.type() == QEvent.Type.MousePress:
            self.do_things(event.position())
    ...


.. code-block:: c++

    bool event(QEvent *event) override
    {
        if (event->type() == QEvent::MousePress) {
            auto *mouseEvent = static_cast<QMouseEvent *>(event);
            doThings(mouseEvent->position());
        ...
    }

The process of determining the type of the event is called `type discovery`.

Shiboken generates code to automatically detect the type. First, it tries to
find a converter for the name obtained by ``typeid(*pointer).name()``. This
should normally work as this name is registered by the binding. If that fails,
it starts walking a type inheritance graph built up in libshiboken to find the
most derived class by using a cast function (``dynamic_cast<>`` by default) to
check.

For normal class hierarchies with virtual destructors, no special handling
is required since ``typeid()`` usually detects the proper class name.

Multiple inheritance
====================

In case of multiple inheritance in C++, the conversion to the derived class is
not done in case it is not a single-line direct inheritance. For example, in
Qt, the class ``QWidget`` inherits both ``QObject`` (base of the ``QObject``
hierarchy) and ``QPaintDevice``.

When calling a function returning a ``QPaintDevice *``, for example
``QPainter.device()``, a Python type representing ``QPaintDevice`` is returned
instead of the underlying widget type. This restriction exists because the
underlying pointer in C++ is a pointer to a ``QPaintDevice *`` and differs from
the pointer to the ``QWidget``.

Hierarchies of classes with non-virtual destructors
===================================================

There are some hierarchies of value-ish C++ classes that do not have virtual
destructors. This makes type discovery based on ``typeid()`` and
``dynamic_cast<>`` impossible.

Examples in Qt are the ``QStyleOption``-derived or the ``QGradient``
-derived classes.

For such classes, some attributes need to be specified on the type entries:

Primarily, a :ref:`polymorphic-id-expression` attribute
must be specified to be used as a check replacing ``dynamic_cast<>``.

In addition, a :ref:`polymorphic-name-function` attribute can be specified.
This replaces the type name guess obtained by ``typeid()`` and is mainly a hint
to speed things up by skipping the checks for each type in the inheritance
graph.

A :ref:`polymorphic-base` attribute identifies the base class of a hierarchy.
It should be given in case the base class inherits from another class to
prevent the logic from going below the base class.

Using type discovery attributes for class hierarchies with virtual destructors
==============================================================================

It is possible to use :ref:`polymorphic-id-expression` and
:ref:`polymorphic-name-function` for normal class hierarchies with virtual
destructors as well since they basically replace ``typeid()`` and
``dynamic_cast<>``. This makes sense if expressions can be specified that are
faster than the checks on virtual tables.

Specifying :ref:`polymorphic-base` can also make sense for generating special
cast functions in case of multiple inheritance. For example, in Qt,
``QWindow``, ``QLayout``, ``QWidget`` are base classes of hierarchies. Since
they all inherit from ``QObject``, indicating the base classes prevents
the logic from using ``QObject`` as a base class.

.. _typediscovery-attributes:

Type discovery attributes reference
===================================

The following attributes related to type discovery may be be specified on the
:ref:`object-type` or :ref:`value-type` elements:

.. _polymorphic-id-expression:

polymorphic-id-expression
+++++++++++++++++++++++++

The **polymorphic-id-expression** attribute specifies an expression checking
whether a base class pointer is of the matching type. For example, in a
``virtual eventHandler(BaseEvent *e)`` function, this is used to construct a
Python wrapper matching the derived class (for example, a ``MouseEvent`` or
similar). The attribute value may contain placeholders:

%1
    Fully qualified class name

%B
    Fully qualified name of the base class (found by base class
    search or as indicated by **polymorphic-base**).

To check for a class inheriting ``BaseEvent``, specify:

.. code-block:: xml

        <object-type name="MouseEvent"
                     polymorphic-id-expression="%B-&gt;type() == BaseEvent::MouseEvent"/>

.. _polymorphic-name-function:

polymorphic-name-function
+++++++++++++++++++++++++

The **polymorphic-name-function** attribute specifies the name of a function
returning the type name of a derived class on the base class type entry.
Normally, ``typeid(ptr).name()`` is used for this.

The function is expected to return ``const char *``.

.. _polymorphic-base:

polymorphic-base
++++++++++++++++

The boolean **polymorphic-base** attribute indicates whether the class is the
base class of a class hierarchy. It is used for the *%B* placeholder in
**polymorphic-id-expression** and for cast operations in multiple inheritance.
