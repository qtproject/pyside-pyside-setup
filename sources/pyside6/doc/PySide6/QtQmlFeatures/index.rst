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
    from PySide6.QtQmlFeatures import load_qml_component

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

The @effect decorator
=====================

``@effect`` marks a method as a side effect that runs whenever any of the
named properties changes. Unlike ``@watch``, an effect does not receive a
:class:`Change`; it is simply called with ``self`` so it can react to the new
state, for example by updating a widget or writing a log entry.

.. decorator:: effect(*property_names)

    :param str property_names: the names of the properties that trigger this
        effect. At least one name is required.

    Returns a decorator that registers the method as an effect of
    *property_names*. The method is invoked as ``method(self)`` after any of
    those properties changes.

The effect is wired up by the ``@auto_properties`` class decorator.

Register the type with ``@QmlElement`` so QML can instantiate it and write
``value``; the ``@effect`` method then runs on the Python side.

Python::

    from PySide6.QtCore import QObject
    from PySide6.QtQml import QmlElement
    from PySide6.QtQmlFeatures import effect, auto_properties

    QML_IMPORT_NAME = "Shop"
    QML_IMPORT_MAJOR_VERSION = 1

    @QmlElement
    @auto_properties
    class Item(QObject):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.value = 0

        @effect("value")
        def on_value_changed(self):
            print(f"value is now {self.value}")

QML:

.. code-block:: javascript

    Item {
        id: item
        // Each slider move writes 'value' from QML; the @effect method
        // then runs on the Python side, printing "value is now <n>".
        Slider { onValueChanged: item.value = value }
    }

An effect that lists several properties runs once for each change to any of
them.

.. _watch-vs-effect:

Comparison: ``@watch`` vs ``@effect``
--------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * -
     - ``@watch``
     - ``@effect``
   * - Properties watched
     - One per decorator (stack to watch more)
     - Many, listed in a single decorator call
   * - Method signature
     - ``(self, change: Change)``
     - ``(self)``
   * - Receives old/new values
     - Yes — via :class:`Change`
     - No

Use ``@watch`` when you need the before/after values; use ``@effect`` when you
only need to react to the new state, for example to persist settings or update
a derived value that does not need :class:`Change` details.

The @auto_properties decorator
==============================

``@auto_properties`` is a class decorator that ties everything together. It
makes a :class:`~PySide6.QtCore.QObject` subclass fully reactive *and*
QML bindable: every reactive member becomes a real
:class:`~PySide6.QtCore.Property` (a ``Q_PROPERTY``) with a change-notification
signal, and every ``@watch``, ``@computed``, and ``@effect`` observer is wired
so its callback runs as a side effect of a property change, including a
change written from QML.

.. decorator:: auto_properties

    Class decorator for a :class:`~PySide6.QtCore.QObject` subclass. Returns
    the same class, augmented in place. Raises :class:`TypeError` if applied to
    a class that is not derived from :class:`~PySide6.QtCore.QObject`.

It recognises three sources of reactive state on the class:

* **Plain assignments in** ``__init__``. For every ``self.<name> = <value>``
  it builds a property ``<name>`` backed by a private attribute, together with
  a ``<name>Changed`` signal.
* **Native Python** ``@property`` **declarations** are converted into a
  :class:`~PySide6.QtCore.Property`, reusing your getter and setter and adding a
  ``<name>Changed`` signal. A getter-only ``@property`` becomes a read-only
  property: writing it (including from QML) raises, and no signal is created.
* **Existing** :class:`~PySide6.QtCore.Property` **declarations** are left exactly
  as you declared them. Their setter is wrapped only when a ``@watch``,
  ``@effect``, or ``@computed`` refers to the property, so the observer
  callbacks run on change; the notify signal stays the one you declared.

The Qt type of a generated or converted property is inferred so that QML sees
a precise type wherever possible: built-in Python types map to their Qt
counterparts (``int``, ``float`` -> ``double``, ``bool``, ``str`` ->
``QString``), ``list`` and ``dict`` become ``QVariantList`` and ``QVariantMap``,
and anything else falls back to ``QVariant``. For an ``__init__`` attribute the
type comes from the assigned default value; for a ``@property`` or ``@computed``
it comes from the getter's ``return`` annotation.

Attribute names starting with an underscore are left untouched, and a name that
is explicitly declared as a property always wins over an ``__init__`` guess of
the same name. Applying ``@auto_properties`` twice to the same class is a no-op.

With ``@auto_properties`` you write ordinary attribute assignments on a type
registered with ``@QmlElement``, and QML can both read and write them, with the
observers firing on every change. Stack the decorators so ``@auto_properties``
runs first (innermost): it must add the generated ``Q_PROPERTY`` objects to the
``QMetaObject`` before ``@QmlElement`` registers the type with the QML engine.

Python::

    from PySide6.QtCore import QObject
    from PySide6.QtQml import QmlElement
    from PySide6.QtQmlFeatures import auto_properties, watch, computed, Change

    QML_IMPORT_NAME = "Shop"
    QML_IMPORT_MAJOR_VERSION = 1

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

        @watch("price")
        def on_price(self, change: Change):
            print(f"price changed to {change.new}")

QML:

.. code-block:: javascript

    import Shop

    Cart {
        id: cart
        // Reads the generated 'price'/'quantity' properties and the
        // @computed 'total'; re-evaluates whenever any of them changes.
        Text { text: "Total: " + cart.total }
        // Writing 'price' from QML runs the generated setter, which fires
        // the @watch callback, invalidates 'total', and emits priceChanged.
        Button { onClicked: cart.price += 1 }
    }

Because ``price`` and ``quantity`` are real ``Q_PROPERTY`` objects with notify
signals, the QML binding above set on ``cart.price`` runs the generated setter,
which fires the ``@watch`` callback, invalidates ``total``, and emits
``priceChanged`` so any QML binding reading the value refreshes.

Loading QML components from Python
==================================

``load_qml_component`` loads a QML component - a custom ``.qml`` file or a type
from a QML module so it can be instantiated and driven entirely from
Python, with no QML glue code.

.. class:: load_qml_component(engine, source=None, *, module=None, type_name=None)

    Loads a QML component and returns a factory for it. Pass a
    :class:`~PySide6.QtQml.QQmlEngine` (or
    :class:`~PySide6.QtQml.QQmlApplicationEngine`) as the first argument.
    Supply exactly one of ``source`` (a path to a ``.qml`` file, absolute
    or relative to the calling ``.py`` file) or both ``module`` (a QML
    module URI such as ``"QtQuick.Controls"``) and ``type_name`` (a type
    within it, such as ``"Slider"``). The returned object is a factory
    whose ``create()`` builds instances.

The factory is lightweight. The actual QML loading and object creation
happens in ``create(**initial_properties)``, which returns a wrapper whose
QML properties, signals, and methods are exposed as plain Python
attributes::

    from PySide6.QtQml import QQmlApplicationEngine
    from PySide6.QtQmlFeatures import load_qml_component

    engine = QQmlApplicationEngine()

    Person = load_qml_component(engine, "person.qml")
    alice = Person.create(name="Alice", age=28)

    alice.age = 29                       # write a QML property
    print(alice.name)                    # read a QML property
    alice.birthdayHappened.connect(...)  # connect to a QML signal
    alice.celebrateBirthday()            # call a QML method
    raw = alice.qobject                  # underlying QObject escape hatch

Assigning a wrapper to a QML property that expects a ``QObject`` (for
example a parent item) unwraps it automatically.

.. note:: Calling a QML method currently returns a success flag rather
    than the method's return value.

See the :ref:`example_qml_qmlcomponentloading` example for a full,
runnable program.
