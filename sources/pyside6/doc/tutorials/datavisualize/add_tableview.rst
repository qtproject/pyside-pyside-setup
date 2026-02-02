.. _tutorial_add_tableview:


Chapter 4 - Add a QTableView
=============================

Now that you have a QMainWindow, you can include a centralWidget to your
interface. Usually, a QWidget is used to display data in most data-driven
applications. Use a table view to display your data.

The first step is to add a horizontal layout with just a
:class:`~PySide6.QtWidgets.QTableView`. You can create a QTableView object
and place it inside a :class:`~PySide6.QtWidgets.QHBoxLayout`. Once the
QWidget is properly built, pass the object to the QMainWindow as its central
widget.

Remember that a QTableView needs a model to display information. In this case,
you can use a :class:`~PySide6.QtCore.QAbstractTableModel` instance.

.. note:: You could also use the default item model that comes with a
   :class:`~PySide6.QtWidgets.QTableWidget` instead. QTableWidget is a
   convenience class that reduces your codebase considerably as you don't need
   to implement a data model. However, it's less flexible than a QTableView,
   as QTableWidget cannot be used with just any data. For more insight about
   Qt's model-view framework, refer to the
   `Model View Programming <https://doc.qt.io/qt-6/model-view-programming.html>`
   documentation.

Implementing the model for your QTableView, allows you to:
- set the headers,
- manipulate the formats of the cell values (remember we have UTC time and float
numbers),
- set style properties like text alignment,
- and even set color properties for the cell or its content.

To subclass the QAbstractTable, you must reimplement its virtual methods,
rowCount(), columnCount(), and data(). This way, you can ensure that the data
is handled properly. In addition, reimplement the headerData() method to
provide the header information to the view.

Here is a script that implements the CustomTableModel:

.. literalinclude:: datavisualize4/table_model.py
   :language: python
   :linenos:
   :lines: 5-

Now, create a QWidget that has a QTableView, and connect it to your
CustomTableModel.

.. literalinclude:: datavisualize4/main_widget.py
   :language: python
   :linenos:
   :emphasize-lines: 12-12
   :lines: 5-

You also need minor changes to the :code:`main_window.py` and
:code:`main.py` from chapter 3 to include the Widget inside the
MainWindow.

In the following snippets you'll see those changes highlighted:

.. literalinclude:: datavisualize4/main_window.py
   :language: python
   :linenos:
   :lines: 5-
   :emphasize-lines: 9

.. literalinclude:: datavisualize4/main.py
   :language: python
   :linenos:
   :lines: 5-
   :emphasize-lines: 45-46
