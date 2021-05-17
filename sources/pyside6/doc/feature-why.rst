.. _features-why:

Why do we have a __feature__?
=============================


History
-------

In PySide user story PYSIDE-1019, we tested certain ways to
make PySide more pythonic. The first idea was to support some
way to allow for ``snake_case`` function names.

This feature is possible with relatively low compatibility
problems, because having the same function with different names
would be not so nice, but a possible low-effort solution.

When going to ``true_property``, things become different. When we
support properties as first class objects instead of getter
and setter functions, we get a conflict, because a function
cannot act as a property (no braces) and be a function at the
same time.

This consideration led us to the idea:
Features must be selectable per-module.


Why are features selectable per-module?
---------------------------------------

Suppose you have some pre-existing code. Maybe you use some downloaded
code or you generated an interface file. When you now decide to
use a feature, you don't want all this existing stuff to become
incorrect. By using the statement

.. code-block:: python

    from __feature__ import ...

you declare that this module uses some feature. Other modules will not
be influenced by this decision and can stay unchanged.


Why dunder, and why not __future__?
-----------------------------------

Especially in Python 2, but in a few cases also in Python 3, there is
the future statement

.. code-block:: python

    from __future__ import ...

That is a statement that can only appear at the beginning of a module,
and it switches how the Python parser works.

Our first idea was to mimick this behavior for PySide, although we are
a bit cheating: The feature statement is not a syntactical construct,
and we cannot easily forbid that it is in the middle of a module.

We then realized that the intention of Python's ``__future__`` import and
PySide's ``__feature__`` import are different: While Python implies by
``__future__`` some improvement, we do not want to associate with
``__feature__``. We simply think that some users who come from Python may
like our features, while others are used to the C++ convention and
consider something that deviates from the Qt documentation as drawback.

The intention to use the ``from __feature__ import ...`` notation was the hope that
people see the similarity to Python's ``__future__`` statement and put that import
at the beginning of a module to make it very visible that this module
has some special global differences.


The snake_case feature
======================

By using the statement

.. code-block:: python

    from __feature__ import snake_case

all methods of all classes used in this module are changing their name.

The algorithm to change names is this:

 * if the name has less than 3 chars, or
 * if two upper chars are adjacent, or
 * if the name starts with ``gl`` (which marks OpenGL),
 * the name is returned unchanged. Otherwise

 * a single upper char ``C`` is replaced by ``_c``


The true_property feature
=========================

By using the statement

.. code-block:: python

    from __feature__ import true_property

all methods of all classes used in this module which are declared in the Qt
documentation as property become real properties in Python.

This feature is incompatible with the past and cannot coexist; it is
the reason why the feature idea was developed at all.


Normal Properties
-----------------

Normal properties have the same name as before:

.. code-block:: python

    QtWidgets.QLabel().color()

becomes as property

.. code-block:: python

    QtWidgets.QLabel().color

When there is also a setter method,

.. code-block:: python

    QtWidgets.QLabel().setColor(value)

becomes as property

.. code-block:: python

    QtWidgets.QLabel().color = value

Normal properties swallow the getter and setter functions and replace
them by the property object.


Special Properties
------------------

Special properties are those with non-standard names.

.. code-block:: python

    QtWidgets.QLabel().size()

becomes as property

.. code-block:: python

    QtWidgets.QLabel().size

But here we have no setSize function, but

.. code-block:: python

    QtWidgets.QLabel().resize(value)

which becomes as property

.. code-block:: python

    QtWidgets.QLabel().size = value

In that case, the setter does not become swallowed, because so many
people are used to the ``resize`` function.


Class properties
----------------

It should be mentioned that we not only support regular properties
as they are known from Python. There is also the concept of class
properties which always call their getter and setter:

A regular property like the aforementioned ``QtWidgets.QLabel`` has
this visibility:

.. code-block:: python

    >>> QtWidgets.QLabel.size
    <property object at 0x113a23540>
    >>> QtWidgets.QLabel().size
    PySide6.QtCore.QSize(640, 480)

A class property instead is also evaluated without requiring an instance:

.. code-block:: python

    >>> QtWidgets.QApplication.windowIcon
    <PySide6.QtGui.QIcon(null) at 0x113a211c0>

You can only inspect it if you go directly to the right class dict:

.. code-block:: python

    >>> QtGui.QGuiApplication.__dict__["windowIcon"]
    <PySide6.PyClassProperty object at 0x114fc5270>


About Property Completeness
---------------------------

There are many properties where the Python programmer agrees that these
functions should be properties, but a few are not properties, like

.. code-block:: python

    >>> QtWidgets.QMainWindow.centralWidget
    <method 'centralWidget' of 'PySide6.QtWidgets.QMainWindow' objects>

We are currently discussing if we should correct these rare cases, as they
are probably only omissions. Having to memorize the missing properties
seems to be quite cumbersome, and instead of looking all properties up in
the Qt documentation, it would be easier to add all properties that
should be properties and are obviously missing.


The __feature__ import
======================

The implementation of ``from __feature__ import ...`` is built by a slight
modification of the ``__import__`` builtin. We made that explicit by assigning
variables in the builtin module. This modification takes place at |project|
import time:

* The original function in ``__import__`` is kept in ``__orig_import__``.
* The new function is in ``__feature_import__`` and assigned to ``__import__``.

This function calls the Python function ``PySide6.support.__feature__.feature_import``
first, and falls back to ``__orig_import__`` if feature import is not applicable.


Overriding __import__
---------------------

This is not recommended. Import modifications should be done using import hooks,
see the Python documentation on `Import-Hooks`_.

If you would like to modify ``__import__`` anyway without destroying the features,
please override just the ``__orig_import__`` function.


IDEs and Modifying Python stub files
------------------------------------

|project| comes with pre-generated ``.pyi`` stub files in the same location as
the binary module. For instance, in the site-packages directory, you can find
a ``QtCore.pyi`` file next to ``QtCore.abi3.so`` or ``QtCore.pyd`` on Windows.

When using ``__feature__`` often with common IDEs, you may want to provide
a feature-aware version of ``.pyi`` files to get a correct display. The simplest
way to change them all in-place is the command

.. code-block:: python

    pyside6-genpyi all --feature snake_case true_property


.. _`Import-Hooks`:  https://docs.python.org/3/reference/import.html#import-hooks
