.. module:: PySide6.QtQmlFeatures

PySide6.QtQmlFeatures
*********************

.. note:: Qt QML Features in 6.12 is in *Technology Preview*, excluding its
          API from Qt's compatibility promises (see :ref:`Qt-Releases`).

The Qt QML Features module provides a small reactive property system for
:class:`~PySide6.QtCore.QObject` subclasses. It lets you observe property
changes, derive values that recompute automatically, and run side effects
when a property changes, all from plain Python code.

The building block is the :class:`Change` type, which describes a single
property change. On top of it the module provides a set of method and class
decorators: ``@watch``, ``@computed``, ``@effect``, and ``@auto_properties``.

To use the module, import the names you need from it::

    from PySide6.QtQmlFeatures import Change, watch, computed, effect

The Change type
===============

A :class:`Change` is an immutable record of one property change. It is the
object passed to every ``@watch`` callback and carries the property name, the
value before the change, the value after the change, and the object that owns
the property.

.. class:: Change(name, old, new, owner)

    :param str name: the name of the property that changed.
    :param object old: the value the property held before the change.
    :param object new: the value the property holds after the change.
    :param object owner: the object whose property changed.

    The constructor arguments are available as the read-only attributes
    ``name``, ``old``, ``new``, and ``owner``.

For example, creating a change for a ``price`` property that went from ``10``
to ``20`` looks like this::

    from PySide6.QtQmlFeatures import Change

    change = Change(name="price", old=10, new=20, owner=cart)
    print(change.name, change.old, change.new)   # price 10 20

You normally do not construct :class:`Change` objects yourself; the reactive
property system creates one and hands it to your ``@watch`` callbacks whenever
an observed property changes.

The @watch decorator
====================

``@watch`` marks a method as an observer of a single property. When that
property changes, the method is called with a :class:`Change` describing what
happened. The decorated method must accept the change object in addition to
``self``.

.. decorator:: watch(property_name)

    :param str property_name: the name of the property to observe.

    Returns a decorator that registers the method as a watcher of
    *property_name*. The method is invoked as ``method(self, change)`` after
    the property changes, where *change* is a :class:`Change` instance.

The observers are wired up by the ``@auto_properties`` class decorator;
``@watch`` on its own only records the property name on the method.

Register the type with ``@QmlElement`` so QML can instantiate it and write
``price``; the ``@watch`` callback then runs on the Python side.

Python::

    from PySide6.QtCore import QObject
    from PySide6.QtQml import QmlElement
    from PySide6.QtQmlFeatures import watch, Change, auto_properties

    QML_IMPORT_NAME = "Shop"
    QML_IMPORT_MAJOR_VERSION = 1

    @QmlElement
    @auto_properties
    class Cart(QObject):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.price = 10

        @watch("price")
        def on_price_changed(self, change: Change):
            print(f"{change.name}: {change.old} -> {change.new}")

QML:

.. code-block:: javascript

    Cart {
        id: cart
        // Clicking writes 'price' from QML; the @watch callback then runs
        // on the Python side, printing "price: 10 -> 11".
        Button { onClicked: cart.price += 1 }
    }

A ``@watch`` callback is only invoked when the value actually changes; setting
a property to its current value does not trigger it.

The @computed decorator
=======================

``@computed`` turns a method into a derived, read-only property. The method
computes a value from one or more other properties, named as the decorator's
arguments. The result is cached and recomputed only when one of those
dependencies changes.

.. decorator:: computed(*dep_names)

    :param str dep_names: the names of the properties this value depends on.
        At least one name is required.

    Returns a decorator that registers the method as a computed property whose
    value depends on *dep_names*. Reading the property returns the cached value,
    recomputing it when any dependency has changed since the last read.

Like ``@watch``, ``@computed`` records its metadata on the method; the
dependency tracking is wired up by the ``@auto_properties`` class decorator.

When a dependency changes, the computed property's ``Changed`` signal is
emitted automatically. This means QML bindings that read the computed
property are notified and re-evaluated just like any other Qt property.

Python::

    @QmlElement
    @auto_properties
    class Cart(QObject):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.price = 10
            self.quantity = 2

        @computed("price", "quantity")
        def total(self):
            return self.price * self.quantity

QML:

.. code-block:: javascript

    Cart { id: cart }
    // Automatically re-evaluates whenever price or quantity changes
    Text { text: "Total: " + cart.total }
    Button { onClicked: cart.price += 1 }
