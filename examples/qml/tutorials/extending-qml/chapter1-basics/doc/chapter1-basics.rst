Extending QML - Creating a New Type
===================================

This is the first of a series of 6 examples forming a tutorial
about extending QML with Python.

The Qt QML module provides a set of APIs for extending QML through Python
extensions. You can write extensions to add your own QML types, extend existing
Qt types, or call Python functions that are not accessible from ordinary QML
code.

This tutorial shows how to write a QML extension using Python that includes
core QML features, including properties, signals and bindings. It also shows
how extensions can be deployed through plugins.

A common task when extending QML is to provide a new QML type that supports
some custom functionality beyond what is provided by the built-in Qt Quick
types. For example, this could be done to implement particular data models, or
provide types with custom painting and drawing capabilities, or access system
features like network programming that are not accessible through built-in QML
features.

In this tutorial, we will show how to use the C++ classes in the Qt Quick
module to extend QML. The end result will be a simple Pie Chart display
implemented by several custom QML types connected together through QML features
like bindings and signals, and made available to the QML runtime through a
plugin.

To begin with, let's create a new QML type called ``PieChart`` that has two
properties: a name and a color. We will make it available in an importable type
namespace called ``Charts``, with a version of 1.0.

We want this ``PieChart`` type to be usable from QML like this:

.. code-block:: javascript

    import Charts 1.0

    PieChart {
        width: 100; height: 100
        name: "A simple pie chart"
        color: "red"
    }

To do this, we need a C++ class that encapsulates this ``PieChart`` type and
its two properties. Since QML makes extensive use of Qt's Meta-Object System
this new class must:

* Inherit from ``QObject``
* Declare its properties using the ``Property`` decorator

Class Implementation
--------------------

Here is our ``PieChart`` class, defined in ``basics.py``:

.. literalinclude:: basics.py
    :lineno-start: 21
    :lines: 21-51

The class inherits from ``QQuickPaintedItem`` because we want to override
``QQuickPaintedItem.paint()`` to perform drawing operations with the
``QPainter`` API. If the class just represented some data type and was not an
item that actually needed to be displayed, it could simply inherit from
``QObject``. Or, if we want to extend the functionality of an existing
``QObject``-based class, it could inherit from that class instead.
Alternatively, if we want to create a visual item that doesn't need to perform
drawing operations with the ``QPainter`` API, we can just subclass
``QQuickItem``.

The ``PieChart`` class defines the two properties, ``name`` and ``color``, with
the ``Property`` decorator, and overrides ``QQuickPaintedItem.paint()``. The
``PieChart`` class is registered using the ``QmlElement`` decorator, to allow
it to be used from QML. If you don't register the class, ``app.qml`` won't be
able to create a ``PieChart``.

QML Usage
---------

Now that we have defined the ``PieChart`` type, we will use it from QML. The
``app.qml`` file creates a ``PieChart`` item and displays the pie chart's details
using a standard QML ``Text`` item:

.. literalinclude:: app.qml
    :lineno-start: 7
    :lines: 7-26

Notice that although the color is specified as a string in QML, it is
automatically converted to a ``QColor`` object for the PieChart ``color``
property. Automatic conversions are provided for various other QML value types.
For example, a string like "640x480" can be automatically converted to a
``QSize`` value.

We'll also create a main function that uses a ``QQuickView`` to run and display
``app.qml``. Here is the application ``basics.py``:

.. literalinclude:: basics.py
    :lineno-start: 54
    :lines: 54-68

.. note:: You may see a warning `Expression ... depends on non-NOTIFYable properties:
    PieChart.name`. This happens because we add a binding to the writable ``name``
    property, but haven't yet defined a notify signal for it. The QML engine therefore
    cannot update the binding if the ``name`` value changes. This is addressed in
    the following chapters.
