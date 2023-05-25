.. currentmodule:: PySide2.QtCore
.. _Property:

Property
********

Detailed Description
--------------------

The Property function lets you declare properties that
behave both as Qt and Python properties, and have their
getters and setters defined as Python functions.

They are equivalent to the ``Q_PROPERTY`` macro in the `Qt Docs`_.

Here is an example that illustrates how to use this
function:

.. code-block::
   :linenos:

    from PySide2.QtCore import QObject, Property

    class MyObject(QObject):
        def __init__(self, startval=42):
            QObject.__init__(self)
            self.ppval = startval

        def readPP(self):
            return self.ppval

        def setPP(self, val):
            self.ppval = val

        pp = Property(int, readPP, setPP)

    obj = MyObject()
    obj.pp = 47
    print(obj.pp)

The full options for ``QtCore.Property`` can be found with ``QtCore.Property.__doc__``:

.. code-block::

   Property(self, type: type,
            fget: Optional[Callable] = None,
            fset: Optional[Callable] = None,
            freset: Optional[Callable] = None,
            fdel: Optional[Callable] = None,
            doc: str = '', notify: Optional[Callable] = None,
            designable: bool = True, scriptable: bool = True,
            stored: bool = True, user: bool = False,
            constant: bool = False, final: bool = False) -> PySide2.QtCore.Property

Normally, only ``type``, ``fget``and ``fset`` are used.


Properties compared with Python properties
------------------------------------------

``Python`` has property objects very similar to ``QtCore.Property``.
Despite the fact that the latter has an extra ``freset`` function, the usage
of properties is almost the same. The main difference is that ``QtCore.Property``
requires a ``type`` parameter.

In the above example, the following lines would be equivalent properties:

.. code-block::

        pp = QtCore.Property(int, readPP, setPP)    # PySide version
        pp = property(readPP, setPP)                # Python version

As you know from the `Python Docs`_, ``Python`` allows to break the property
creation into multiple steps, using the decorator syntax. We can do this in
``PySide`` as well:

.. code-block::
   :linenos:

    from PySide2.QtCore import QObject, Property

    class MyObject(QObject):
        def __init__(self, startval=42):
            QObject.__init__(self)
            self.ppval = startval

        @Property(int)
        def pp(self):
            return self.ppval

        @pp.setter
        def pp(self, val):
            self.ppval = val

    obj = MyObject()
    obj.pp = 47
    print(obj.pp)

Please be careful here: The two ``Python`` functions have the same name, intentionally.
This is needed to let ``Python`` know that these functions belong to the same property.


Properties in QML expressions
-----------------------------

If you are using properties of your objects in QML expressions,
QML requires that the property changes are notified. Here is an
example illustrating how to do this:

.. code-block::
   :linenos:

    from PySide2.QtCore import QObject, Signal, Property

    class Person(QObject):
        def __init__(self, name):
            QObject.__init__(self)
            self._person_name = name

        def _name(self):
            return self._person_name

        @Signal
        def name_changed(self):
            pass

        name = Property(str, _name, notify=name_changed)

.. _`Python Docs`:  https://docs.python.org/3/library/functions.html?highlight=property#property
.. _`Qt Docs`:  https://doc.qt.io/qt-5/properties.html
