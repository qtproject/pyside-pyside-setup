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
