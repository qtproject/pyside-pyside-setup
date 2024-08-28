.. _getting-started:

Getting Started
===============

Here you can find the steps to install and create a simple application
using the two technologies that Qt provides: Qt Widgets and Qt Quick.

.. note:: If you are new to Qt, you can check the :ref:`faq-section` section at
   the end of this page to understand concepts, file types, compatibles IDEs,
   etc.  In case you own a Qt License, please refer to :ref:`commercial-page`.

Requirements
------------

Before you can install |project|, first you must install the following software:

* `Official <https://www.python.org/downloads/>`_ Python 3.8+
* We **highly** recommend using a virtual environment, such as
  `venv <https://docs.python.org/3/library/venv.html>`_ or
  `virtualenv <https://virtualenv.pypa.io/en/latest>`_
  and avoid installing PySide6 via ``pip`` in your system.

Installation
------------

* **Creating and activating an environment**
  You can do this by running the following on a terminal:

  * Create environment (Your Python executable might be called ``python3``)::

        python -m venv env

  * Activate the environment (Linux and macOS)::

        source env/bin/activate

  * Activate the environment (Windows)::

        env\Scripts\activate.bat

  Check this animation on how to do it:

  .. image:: https://qt-wiki-uploads.s3.amazonaws.com/images/8/8a/Pyside6_install.gif
     :alt: PySide6 Installation GIF

  .. note:: Having Qt installed in your system will not interfere with your
     PySide6 installation if you do it via ``pip install``, because the Python
     packages (wheels) already includes Qt binaries. Most notably, style plugins
     from the system won't have any effect on PySide applications.


* **Installing PySide6**

  .. note:: For a commercial installation, refer to :ref:`commercial-page`.

  Now you are ready to install the |project| packages using ``pip``.
  From the terminal, run the following command:

  * For the latest version::

        pip install pyside6

  * For a specific version, like 6.4.1::

        pip install pyside6==6.4.1

  * It is also possible to install a specific snapshot from our servers.
    To do so, you can use the following command::

      pip install --index-url=https://download.qt.io/snapshots/ci/pyside/6.4/latest pyside6 --trusted-host download.qt.io

* **Test your installation**

  Now that you have |project| installed, test your setup by running the following Python
  constructs to print version information::

    import PySide6.QtCore

    # Prints PySide6 version
    print(PySide6.__version__)

    # Prints the Qt version used to compile PySide6
    print(PySide6.QtCore.__version__)

  .. note:: For more information about what's included in the ``pyside6``
     package, check :ref:`package_details`.


Create your first Qt Application
--------------------------------

.. image:: https://qt-wiki-uploads.s3.amazonaws.com/images/e/eb/Pyside6_widgets_quick.gif
   :alt: Qt Widgets and Qt Quick comparison header animation

Qt provides two technologies to build User Interfaces:

* Qt Widgets, an imperative programming and design approach that has been
  around since the beginning of Qt, making it a stable and reliable technology
  for UI applications.
* Qt Quick, a declarative programming and design approach, which enables you to
  create fluid UIs by describing them in terms of simple elements.

Both technologies offer you the possibility to use *drag and drop* tools
to create your interfaces. :ref:`pyside6-designer` for Qt Widgets (included
when you install pyside6), and Qt Design Studio for Qt Quick (`Get it here`_).

.. note:: After reading this page, it is recommended that you check the
   :ref:`pyside6-project` tool to learn how to create projects automatically
   without writing all the code by hand.

.. _`Get it here`: https://doc.qt.io/qt-6/install-qt-design-studio.html

Create your first Qt Application with Qt Widgets
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Your |project| setup is ready. You can explore it further by developing a simple application
that prints ``"Hello World"`` in several languages. The following instructions will
guide you through the development process:

* **Imports**

  Create a new file named :code:`hello_world.py`, and add the following imports to it.::

    import sys
    import random
    from PySide6 import QtCore, QtWidgets, QtGui

  The |pymodname| Python module provides access to the Qt APIs as its submodule.
  In this case, you are importing the :ref:`QtCore`, :ref:`QtWidgets`, and :ref:`QtGui` submodules.

* **Main Class**

  Define a class named :code:`MyWidget`, which extends :ref:`QWidget` and
  includes a :ref:`QPushButton` and :ref:`QLabel`.::

    class MyWidget(QtWidgets.QWidget):
        def __init__(self):
            super().__init__()

            self.hello = ["Hallo Welt", "Hei maailma", "Hola Mundo", "Привет мир"]

            self.button = QtWidgets.QPushButton("Click me!")
            self.text = QtWidgets.QLabel("Hello World",
                                         alignment=QtCore.Qt.AlignCenter)

            self.layout = QtWidgets.QVBoxLayout(self)
            self.layout.addWidget(self.text)
            self.layout.addWidget(self.button)

            self.button.clicked.connect(self.magic)

        @QtCore.Slot()
        def magic(self):
            self.text.setText(random.choice(self.hello))

  The ``MyWidget`` class has the :code:`magic` member function that randomly
  chooses an item from the :code:`hello` list. When you click the button, the
  :code:`magic` function is called.

* **Application execution**

  Now, add a main function where you instantiate :code:`MyWidget` and :code:`show` it.::

    if __name__ == "__main__":
        app = QtWidgets.QApplication([])

        widget = MyWidget()
        widget.resize(800, 600)
        widget.show()

        sys.exit(app.exec())

  Run your example by writing the following command:

  .. code-block:: bash

    python hello_world.py

  Try clicking the button at the bottom to see which greeting you get.

  .. image:: images/screenshot_hello_widgets.png
     :alt: Hello World application in Qt Widgets

Create your first Qt Application with Qt Quick
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To do the same using Qt Quick:

* **Imports**

  Create a new file named :code:`hello_world_quick.py`, and add the following imports to it.::

    import sys
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtQml import QQmlApplicationEngine

* **Declarative UI**

  The UI can be described in the QML language:

  .. code-block:: javascript

    import QtQuick
    import QtQuick.Controls
    import QtQuick.Layouts

    Window {
        width: 300
        height: 200
        visible: true
        title: "Hello World"

        readonly property list<string> texts: ["Hallo Welt", "Hei maailma",
                                               "Hola Mundo", "Привет мир"]

        function setText() {
            var i = Math.round(Math.random() * 3)
            text.text = texts[i]
        }

        ColumnLayout {
            anchors.fill:  parent

            Text {
                id: text
                text: "Hello World"
                Layout.alignment: Qt.AlignHCenter
            }
            Button {
                text: "Click me"
                Layout.alignment: Qt.AlignHCenter
                onClicked:  setText()
            }
        }
    }

  Put the this into a file named :code:`Main.qml` into a directory named
  :code:`Main` along with a file named :code:`qmldir` to describe a basic
  QML module:

  .. code-block:: text

    module Main
    Main 254.0 Main.qml

* **Application execution**

  Now, add a main function where you instantiate a :ref:`QQmlApplicationEngine` and
  load the QML::

    import sys
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtQml import QQmlApplicationEngine

    if __name__ == "__main__":
        app = QGuiApplication(sys.argv)
        engine = QQmlApplicationEngine()
        engine.addImportPath(sys.path[0])
        engine.loadFromModule("Main", "Main")
        if not engine.rootObjects():
            sys.exit(-1)
        exit_code = app.exec()
        del engine
        sys.exit(exit_code)

  Run your example by writing the following command:

  .. code-block:: bash

    python main.py


  Try clicking the button at the bottom to see which greeting you get.

  .. image:: images/screenshot_hello_quick.png
     :alt: Hello World application in Qt Quick

Next steps
----------

Now that you have use both technologies, you can head to our
:ref:`pyside6_examples` and :ref:`pyside6_tutorials` sections.

.. _faq-section:

Frequently Asked Questions
--------------------------

Here you can find a couple of common questions and situations that will
clarify questions before you start programming.

.. grid:: 1 3 3 3
    :gutter: 2

    .. grid-item-card:: What is Qt
        :link: whatisqt
        :link-type: ref

        Qt, QML, Widgets... What is the difference?

    .. grid-item-card:: Compatible IDEs
        :link: whichide
        :link-type: ref

        Which IDEs are compatible with PySide?

    .. grid-item-card:: Binding Generation
        :link: whatisshiboken
        :link-type: ref

        What is Shiboken?

    .. grid-item-card:: File types
        :link: typesoffiles
        :link-type: ref

        File Types in PySide

    .. grid-item-card:: App distribution
        :link: distribution
        :link-type: ref

        Distributing your application to other systems and platforms

    .. grid-item-card:: Why Qt for Python?
        :link: whyqtforpython
        :link-type: ref

        As a Qt/C++ developer, why should I consider Qt for Python?

.. toctree::
    :hidden:

    faq/whatisqt.rst
    faq/whichide.rst
    faq/whatisshiboken.rst
    faq/typesoffiles.rst
    faq/distribution.rst
    faq/whyqtforpython.rst
    faq/porting_from2.rst

