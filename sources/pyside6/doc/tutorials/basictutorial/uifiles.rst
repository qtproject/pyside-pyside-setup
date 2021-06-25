Using `.ui` files from Designer or QtCreator with `QUiLoader` and `pyside6-uic`
*******************************************************************************

This page describes the use of
`Qt Designer <https://doc.qt.io/qt-6/qtdesigner-manual.html>`_ to create
graphical interfaces based on Qt Widgets for your Qt for Python project.
**Qt Designer** is a graphical UI design tool which is available as a
standalone binary (``pyside6-designer``) or embedded into the
`Qt Creator IDE <https://doc.qt.io/qtcreator>`_. Its use within **Qt Creator**
is described at
`Using Qt Designer <http://doc.qt.io/qtcreator/creator-using-qt-designer.html>`_.

The designs are stored in `.ui` files, which is an XML-based format. It will
be converted to Python or C++ code populating a widget instance at project build
time by the `pyside6-uic <https://doc.qt.io/qt-6/uic.html>`_ tool.

To create a new Qt Design Form in **Qt Creator**, choose
`File/New File Or Project` and "Main Window" for template. Save it as
`mainwindow.ui`. Add a `QPushButton` to the center of the centralwidget.

Your file ``mainwindow.ui`` should look something like this:

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
       <widget class="QPushButton" name="pushButton">
        <property name="geometry">
         <rect>
          <x>110</x>
          <y>80</y>
          <width>201</width>
          <height>81</height>
         </rect>
        </property>
        <property name="text">
         <string>PushButton</string>
        </property>
       </widget>
      </widget>
      <widget class="QMenuBar" name="menuBar">
       <property name="geometry">
        <rect>
         <x>0</x>
         <y>0</y>
         <width>400</width>
         <height>20</height>
        </rect>
       </property>
      </widget>
      <widget class="QToolBar" name="mainToolBar">
       <attribute name="toolBarArea">
        <enum>TopToolBarArea</enum>
       </attribute>
       <attribute name="toolBarBreak">
        <bool>false</bool>
       </attribute>
      </widget>
      <widget class="QStatusBar" name="statusBar"/>
     </widget>
     <layoutdefault spacing="6" margin="11"/>
     <resources/>
     <connections/>
    </ui>

Now we are ready to decide how to use the **UI file** from Python.

Option A: Generating a Python class
===================================

The standard way to interact with a **UI file** is to generate a Python
class from it. This is possible thanks to the `pyside6-uic` tool.
To use this tool, you need to run the following command on a console::

    pyside6-uic mainwindow.ui > ui_mainwindow.py

We redirect all the output of the command to a file called `ui_mainwindow.py`,
which will be imported directly::

    from ui_mainwindow import Ui_MainWindow

Now to use it, we should create a personalized class for our widget
to **setup** this generated design.

To understand the idea, let's take a look at the whole code:

.. code-block:: python

    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow
    from PySide6.QtCore import QFile
    from ui_mainwindow import Ui_MainWindow

    class MainWindow(QMainWindow):
        def __init__(self):
            super(MainWindow, self).__init__()
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)

    if __name__ == "__main__":
        app = QApplication(sys.argv)

        window = MainWindow()
        window.show()

        sys.exit(app.exec())

What is inside the *if* statement is already known from the previous
examples, and our new basic class contains only two new lines
that are in charge of loading the generated python class from the UI
file:

.. code-block:: python

    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)

.. note::

  You must run `pyside6-uic` again every time you make changes
  to the **UI file**.

Option B: Loading it directly
=============================

To load the UI file directly, we will need a class from the **QtUiTools**
module:

.. code-block:: python

    from PySide6.QtUiTools import QUiLoader

The `QUiLoader` lets us load the **ui file** dynamically
and use it right away:

.. code-block:: python

    ui_file = QFile("mainwindow.ui")
    ui_file.open(QFile.ReadOnly)

    loader = QUiLoader()
    window = loader.load(ui_file)
    window.show()

The complete code of this example looks like this:

.. code-block:: python

    # File: main.py
    import sys
    from PySide6.QtUiTools import QUiLoader
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QFile, QIODevice

    if __name__ == "__main__":
        app = QApplication(sys.argv)

        ui_file_name = "mainwindow.ui"
        ui_file = QFile(ui_file_name)
        if not ui_file.open(QIODevice.ReadOnly):
            print(f"Cannot open {ui_file_name}: {ui_file.errorString()}")
            sys.exit(-1)
        loader = QUiLoader()
        window = loader.load(ui_file)
        ui_file.close()
        if not window:
            print(loader.errorString())
            sys.exit(-1)
        window.show()

        sys.exit(app.exec())

Then to execute it we just need to run the following on a
command prompt:

.. code-block:: python

    python main.py


.. _designer_custom_widgets:

Custom Widgets in Qt Designer
=============================

**Qt Designer** is able to use user-provided (custom) widgets. They are shown
in the widget box and can be dragged onto the form just like Qt's widgets (see
`Using Custom Widgets with Qt Designer <https://doc.qt.io/qt-6/designer-using-custom-widgets.html>`_
). Normally, this requires implementing the widget as a plugin to Qt Designer
written in  C++ implementing its
`QDesignerCustomWidgetInterface <https://doc.qt.io/qt-6/qdesignercustomwidgetinterface.html>`_ .

Qt for Python provides a simple interface for this which is similar to
:meth:`registerCustomWidget()<PySide6.QtUiTools.QUiLoader.registerCustomWidget>`.

The widget needs to be provided as a Python module, as shown by
the widgetbinding example (file ``wigglywidget.py``) or
the taskmenuextension example (file ``tictactoe.py``).

Registering this with Qt Designer is done by providing
a registration script named ``register*.py`` and pointing
the  path-type environment variable ``PYSIDE_DESIGNER_PLUGINS``
to the directory.

The code of the registration script looks as follows:

.. code-block:: python

    # File: registerwigglywidget.py
    from wigglywidget import WigglyWidget

    import QtDesigner


    TOOLTIP = "A cool wiggly widget (Python)"
    DOM_XML = """
    <ui language='c++'>
        <widget class='WigglyWidget' name='wigglyWidget'>
            <property name='geometry'>
                <rect>
                    <x>0</x>
                    <y>0</y>
                    <width>400</width>
                    <height>200</height>
                </rect>
            </property>
            <property name='text'>
                <string>Hello, world</string>
            </property>
        </widget>
    </ui>
    """

    QPyDesignerCustomWidgetCollection.registerCustomWidget(WigglyWidget, module="wigglywidget",
                                                           tool_tip=TOOLTIP, xml=DOM_XML)


QPyDesignerCustomWidgetCollection provides an implementation of
`QDesignerCustomWidgetCollectionInterface <https://doc.qt.io/qt-6/qdesignercustomwidgetcollectioninterface.html>`_
exposing custom widgets to **Qt Designer** with static convenience functions
for registering types or adding instances of
`QDesignerCustomWidgetInterface <https://doc.qt.io/qt-6/qdesignercustomwidgetinterface.html>`_ .

The function
:meth:`registerCustomWidget()<PySide6.QtDesigner.QPyDesignerCustomWidgetCollection.registerCustomWidget>`
is used to register a widget type with **Qt Designer**. In the simple case, it
can be used like `QUiLoader.registerCustomWidget()`. It takes the custom widget
type and some optional keyword arguments passing values that correspond to the
getters of
`QDesignerCustomWidgetInterface <https://doc.qt.io/qt-6/qdesignercustomwidgetinterface.html>`_ :

When launching **Qt Designer** via its launcher ``pyside6-designer``,
the custom widget should be visible in the widget box.

For advanced usage, it is also possible to pass the function an implementation
of the class QDesignerCustomWidgetInterface instead of the type to
:meth:`addCustomWidget()<PySide6.QtDesigner.QPyDesignerCustomWidgetCollection.addCustomWidget>`.
This is shown in taskmenuextension example, where a custom context menu
is registered for the custom widget. The example is a port of the
corresponding C++
`Task Menu Extension Example <https://doc.qt.io/qt-6/qtdesigner-taskmenuextension-example.html>`_ .

Troubleshooting the Qt Designer Plugin
++++++++++++++++++++++++++++++++++++++

- The launcher ``pyside6-designer`` must be used. The standalone
  **Qt Designer** will not load the plugin.
- The menu item **Help/About Plugin** brings up a dialog showing the plugins
  found and potential load error messages.
- Check the console or Windows Debug view for further error messages.
- Due to the buffering of output by Python, error messages may appear
  only after **Qt Designer** has terminated.
- When building Qt for Python, be sure to set the ``--standalone`` option
  for the plugin to be properly installed.
