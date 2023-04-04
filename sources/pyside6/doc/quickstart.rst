.. _quick-start:

Quick start
===========

New to Qt? Check also the :ref:`faq-section` section at the end of this page.

Requirements
------------

Before you can install |project|, first you must install the following software:

* Python 3.7+,
* We recommend using a virtual environment, such as
  `venv <https://docs.python.org/3/library/venv.html>`_ or
  `virtualenv <https://virtualenv.pypa.io/en/latest>`_

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
     :alt: Installation gif

* **Installing PySide6**

  Now you are ready to install the |project| packages using ``pip``.
  From the terminal, run the following command:

  * For the latest version::

        pip install pyside6

  * For a specific version, like 6.4.1::

        pip install pyside6==6.4.1

  * It is also possible to install a specific snapshot from our servers.
    To do so, you can use the following command::

      pip install --index-url=https://download.qt.io/snapshots/ci/pyside/6.4/latest pyside6 --trusted-host download.qt.io

  .. note:: Starting with 6.4.3, PySide6 can be used from inside a conda
     environment, but any manual changes you make to the qt.conf file will be
     ignored. If you want to set custom values to the Qt configuration, set
     them in a qt6.conf file instead. Read more about `qt.conf`_.

.. _`qt.conf`: https://doc.qt.io/qt-6/qt-conf.html

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

Create a Simple Qt Widgets Application
--------------------------------------

Your |project| setup is ready. You can explore it further by developing a simple application
that prints "Hello World" in several languages. The following instructions will
guide you through the development process:

* **Imports**

  Create a new file named :code:`hello_world.py`, and add the following imports to it.::

    import sys
    import random
    from PySide6 import QtCore, QtWidgets, QtGui

  The |pymodname| Python module provides access to the Qt APIs as its submodule.
  In this case, you are importing the :code:`QtCore`, :code:`QtWidgets`, and :code:`QtGui` submodules.

* **Main Class**

  Define a class named :code:`MyWidget`, which extends QWidget and includes a QPushButton and
  QLabel.::

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

  The MyWidget class has the :code:`magic` member function that randomly chooses an item from the
  :code:`hello` list. When you click the button, the :code:`magic` function is called.

* **Application execution**

  Now, add a main function where you instantiate :code:`MyWidget` and :code:`show` it.::

    if __name__ == "__main__":
        app = QtWidgets.QApplication([])

        widget = MyWidget()
        widget.resize(800, 600)
        widget.show()

        sys.exit(app.exec())

  Run your example by writing the following command: :command:`python hello_world.py`.

  Try clicking the button at the bottom to see which greeting you get.

  .. image:: images/screenshot_hello.png
     :alt: Hello World application

Create a Simple Quick Application
---------------------------------

To do the same using Qt Quick:

* **Imports**

  Create a new file named :code:`hello_world_quick.py`, and add the following imports to it.::

    import sys
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtQml import QQmlApplicationEngine

* **Declarative UI**

  The UI can be described in the QML language (assigned to a Python variable)::

    QML = """
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
    """

* **Application execution**

  Now, add a main function where you instantiate a :code:`QQmlApplicationEngine` and
  load the QML::

    if __name__ == "__main__":
        app = QGuiApplication(sys.argv)
        engine = QQmlApplicationEngine()
        engine.loadData(QML.encode('utf-8'))
        if not engine.rootObjects():
            sys.exit(-1)
        exit_code = app.exec()
        del engine
        sys.exit(exit_code)


  .. note:: This is a simplified example. Normally, the QML code should be in a separate
     :code:`.qml` file, which can be edited by design tools.

.. _faq-section:

Frequently Asked Questions
--------------------------

Here you can find a couple of common questions and situations that will
clarify questions before you start programming.

.. grid:: 1 3 3 3
    :gutter: 2

    .. grid-item-card:: What is Qt
        :link: faq/whatisqt.html

        Qt, QML, Widgets... What is the difference?

    .. grid-item-card:: Compatible IDEs
        :link: faq/whichide.html

        Which IDEs are compatible with PySide?

    .. grid-item-card:: Binding Generation
        :link: faq/whatisshiboken.html

        What is Shiboken?

    .. grid-item-card:: File types
        :link: faq/typesoffiles.html

        File Types in PySide

    .. grid-item-card:: App distribution
        :link: faq/distribution.html

        Distributing your application to other systems and platforms

    .. grid-item-card:: Why Qt for Python?
        :link: faq/whyqtforpython.html

        As a Qt/C++ developer, why should I consider Qt for Python?

.. toctree::
    :hidden:

    faq/whatisqt.rst
    faq/whichide.rst
    faq/whatisshiboken.rst
    faq/typesoffiles.rst
    faq/distribution.rst
    faq/whyqtforpython.rst


