Your First QtQuick/QML Application
**********************************

QML_ is a declarative language that lets you develop applications
faster than with traditional languages. It is ideal for designing the
UI of your application because of its declarative nature. In QML, a
user interface is specified as a tree of objects with properties. In
this tutorial, we will show how to make a simple "Hello World"
application with PySide6 and QML.

A PySide6/QML application consists, mainly, of two different files -
a file with the QML description of the user interface, and a python file
that loads the QML file.

Here is a simple QML file called :code:`Main.qml`:

.. code-block:: javascript

    import QtQuick

    Rectangle {
        id: main
        width: 200
        height: 200
        color: "green"

        Text {
            text: "Hello World"
            anchors.centerIn: main
        }
    }

We start by importing :code:`QtQuick`, which is a QML module.

The rest of the QML code is pretty straightforward for those who
have previously used HTML or XML files. Basically, we are creating
a green rectangle with the size `200*200`, and adding a Text element
that reads "Hello World". The code :code:`anchors.centerIn: main` makes
the text appear centered within the object with :code:`id: main`,
which is the Rectangle in this case.

Put the file into into a directory named :code:`Main` along
with a file named :code:`qmldir` to describe a basic QML module:

.. code-block:: text

    module Main
    Main 254.0 Main.qml

Now, let's see how the code looks on the PySide6.
Let's call it :code:`main.py`:

.. code-block:: python

    import sys
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtQuick import QQuickView

    if __name__ == "__main__":
        app = QGuiApplication()
        view = QQuickView()
        view.engine().addImportPath(sys.path[0])
        view.loadFromModule("Main", "Main")
        view.show()
        ex = app.exec()
        del view
        sys.exit(ex)

If you are already familiar with PySide6 and have followed our
tutorials, you have already seen much of this code.
The only novelties are that you must :code:`import QtQuick`,
add the directory to the import paths, and instruct the
:code:`QQuickView` to load our module.
Then, similar to what you do with any Qt widget, you call
:code:`QQuickView.show()`.

.. note:: If you are programming for desktop, you should consider
    adding `view.setResizeMode(QQuickView.SizeRootObjectToView)`
    before showing the view.

When you execute the :code:`main.py` script, you will see the following
application:


.. image:: greenapplication.png
    :alt: Simple QML and Python example
    :align: center

.. _QML: https://doc.qt.io/qt-6/qmlapplications.html
