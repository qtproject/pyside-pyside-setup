.. _typesoffiles:

File Types
==========

There are many different file types that you will encounter while
developing |project| applications, ui, qrc, qml, pyproject, etc.
Here you can find a simple explanation for
each of them.

Python Files ``.py``
--------------------

Python files are the main format you will be dealing with, while developing
|project| projects.

It is important to note that you can write applications **only** with Python
files, without the need of ``.ui``, ``.qrc``, or ``.qml`` files, however
using other formats will facilitate some processes, and enable new
functionality to your applications.

.. code-block:: python

    class MyWidget(QWidget):
        def __init__(self):
            QWidget.__init__(self)

            self.hello = ["Hallo Welt", "你好，世界", "Hei maailma",
                "Hola Mundo", "Привет мир"]

            self.button = QPushButton("Click me!")
            self.text = QLabel("Hello World")
            self.text.setAlignment(Qt.AlignCenter)
            # ...

User Interface Definition File ``.ui``
--------------------------------------

When using Qt Designer, you can create user interfaces using Qt Widgets with
the WYSIWYG form editor, this interface is represented as a widget tree using
XML. Here is an extract of the beginning of a ``.ui`` file:

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <ui version="4.0">
     <class>MainWindow</class>
     <widget class="QMainWindow" name="MainWindow">
      <property name="geometry">
       <rect>
        <x>0</x>
        <y>0</y>
        <width>400</width>
        <height>300</height>
       </rect>
      </property>
      <property name="windowTitle">
       <string>MainWindow</string>
      </property>
      <widget class="QWidget" name="centralWidget">
    ...

The `pyside6-uic` tool generates Python code from these `.ui` files,
which you can import from your main files, so it is not necessary
for you to include the `.ui` files in your deployed application.

For more details, see :ref:`using_ui_files`.

Resource Collection Files ``.qrc``
----------------------------------

List of binary files that will be used alongside your application.
As an XML-based file, its structure look like this:

.. code-block:: xml

    <!DOCTYPE RCC><RCC version="1.0">
    <qresource>
        <file>images/quit.png</file>
        <file>font/myfont.ttf</file>
    </qresource>
    </RCC>


The `pyside6-rcc` tool generates Python code from these `.qrc` files,
so you are not required to include the listed files in your deployed
application.

For more details, see :ref:`using_qrc_files`.

Qt Modeling Language File ``.qml``
----------------------------------

Graphical QML applications are not related to Qt Widgets applications, and
that is why the usual setup of QML project is a Python file that loads
the QML file, and optionally, elements defined in Python that are exposed
to QML to be used.

You can write ``.qml`` files by hand, but also you can use tools like the
QML Designer that is embedded in Qt Creator. Additionally, there are commercial
tools like Qt Design Studio that allow you to load designs from other design
applications.

Here you can find an example of how a ``.qml`` file looks like.
The code will display a lightgray rectangle, with the "Hello World!"
message on it.

.. code-block:: javascript

    import QtQuick 2.0

    Rectangle {
        id: page
        width: 320;
        height: 480
        color: "lightgray"

        Text {
            id: helloText
            text: "Hello world!"
            y: 30
            anchors.horizontalCenter: page.horizontalCenter
            font.pointSize: 24;
            font.bold: true
        }
    }

Qt Creator Python Project File ``.pyproject``
---------------------------------------------

For Qt Creator to load and handle Python based projects, a special file is
needed, because C++ based projects could be handle from ``.qmake`` or
``CMakeLists.txt`` file, which are not used with Python-based projects.

Old versions of Qt Creator, provided a simple format with the ``.pyqtc``
extension, which were plain-text files with one-file-per-line::

    library/server.py
    library/client.py
    logger.py
    ...

There were limitations to this format, and further options that might be
added that would not be supported, which was the motivation to create a
``.pyproject`` file, which is a JSON-based file where more options could
be added. Here is an example of such file:

.. code-block:: javascript

    {
        "files": ["library/server.py", "library/client.py", "logger.py", ...]
    }
