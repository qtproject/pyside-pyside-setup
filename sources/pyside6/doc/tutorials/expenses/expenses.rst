Expenses Tool Tutorial
======================

In this tutorial you will learn the following concepts:
 * creating user interfaces programatically,
 * layouts and widgets,
 * overloading Qt classes,
 * connecting signal and slots,
 * interacting with QWidgets,
 * and building your own application.

The requirements:
 * A simple window for the application
   (`QMainWindow <https://doc.qt.io/qtforpython/PySide6/QtWidgets/QMainWindow.html>`_).
 * A table to keep track of the expenses
   (`QTableWidget <https://doc.qt.io/qtforpython/PySide6/QtWidgets/QTableWidget.html>`_).
 * Two input fields to add expense information
   (`QLineEdit <https://doc.qt.io/qtforpython/PySide6/QtWidgets/QLineEdit.html>`_).
 * Buttons to add information to the table, plot data, clear table, and exit the application
   (`QPushButton <https://doc.qt.io/qtforpython/PySide6/QtWidgets/QPushButton.html>`_).
 * A verification step to avoid invalid data entry.
 * A chart to visualize the expense data
   (`QChart <https://doc.qt.io/qtforpython/PySide6/QtCharts/QChart.html>`_) that will
   be embedded in a chart view
   (`QChartView <https://doc.qt.io/qtforpython/PySide6/QtCharts/QChartView.html>`_).

Empty window
------------

The base structure for a `QApplication` is located inside the `if __name__ == "__main__":`
code block.

.. code-block:: python
   :linenos:

     if __name__ == "__main__":
         app = QApplication([])
         # ...
         sys.exit(app.exec())

Now, to start the development, create an empty window called `MainWindow`.
You could do that by defining a class that inherits from `QMainWindow`.

.. literalinclude:: steps/01-expenses.py
   :linenos:
   :lines: 8-22
   :emphasize-lines: 1-4

Now that our class is defined, create an instance of it and call `show()`.

.. literalinclude:: steps/01-expenses.py
   :linenos:
   :lines: 8-22
   :emphasize-lines: 10-12

Menu bar
--------

Using a `QMainWindow` gives some features for free, among them a *menu bar*.  To use it, you need
to call the method `menuBar()` and populate it inside the `MainWindow` class.

.. literalinclude:: steps/02-expenses.py
   :linenos:
   :lines: 9-19
   :emphasize-lines: 10

Notice that the code snippet adds a *File* menu with the *Exit* option only.

The *Exit* option must be connected to a slot that triggers the application to exit. We pass
``QWidget.close()`` here. After the last window has been closed, the application exits.

Empty widget and data
---------------------

The `QMainWindow` enables us to set a central widget that will be displayed when showing the window
(`read more <https://doc.qt.io/qt-5/qmainwindow.html#details>`_).
This central widget could be another class derived from `QWidget`.

Additionally, you will define example data to visualize later.

.. literalinclude:: steps/04-expenses.py
   :linenos:
   :lines: 8-15

With the `Widget` class in place, modify `MainWindow`'s initialization code

.. literalinclude:: steps/04-expenses.py
   :linenos:
   :lines: 37-40

Window layout
-------------

Now that the main empty window is in place, you need to start adding widgets to achieve the main
goal of creating an expenses application.

After declaring the example data, you can visualize it on a simple `QTableWidget`.  To do so, you
will add this procedure to the `Widget` constructor.

.. warning:: Only for the example purpose a QTableWidget will be used,
             but for more performance-critical applications the combination
             of a model and a QTableView is encouraged.

.. literalinclude:: steps/05-expenses.py
   :linenos:
   :lines: 11-31

As you can see, the code also includes a `QHBoxLayout` that provides the container to place widgets
horizontally.

Additionally, the `QTableWidget` allows for customizing it, like adding the labels for the two
columns that will be used, and to *stretch* the content to use the whole `Widget` space.

The last line of code refers to *filling the table**, and the code to perform that task is
displayed below.

.. literalinclude:: steps/05-expenses.py
   :linenos:
   :lines: 33-39

Having this process on a separate method is a good practice to leave the constructor more readable,
and to split the main functions of the class in independent processes.


Right side layout
-----------------

Because the data that is being used is just an example, you are required to include a mechanism to
input items to the table, and extra buttons to clear the table's content, and also quit the
application.

For input lines along with descriptive labels, you will use a `QFormLayout`. Then,
you will nest the form layout into a `QVBoxLayout` along with the buttons.

.. literalinclude:: steps/06-expenses.py
   :linenos:
   :lines: 27-43

Leaving the table on the left side and these newly included widgets to the right side
will be just a matter to add a layout to our main `QHBoxLayout` as you saw in the previous
example:

.. literalinclude:: steps/06-expenses.py
   :linenos:
   :lines: 45-48

The next step will be connecting those new buttons to slots.


Adding elements
---------------

Each `QPushButton` have a signal called *clicked*, that is emitted when you click on the button.
This will be more than enough for this example, but you can see other signals in the `official
documentation <https://doc.qt.io/qtforpython/PySide6/QtWidgets/QAbstractButton.html#signals>`_.

.. literalinclude:: steps/07-expenses.py
   :linenos:
   :lines: 50-52

As you can see on the previous lines, we are connecting each *clicked* signal to different slots.
In this example slots are normal class methods in charge of perform a determined task associated
with our buttons. It is really important to decorate each method declaration with a `@Slot()`,
that way, PySide6 knows internally how to register them into Qt and they
will be invokable from `Signals` of QObjects when connected.


.. literalinclude:: steps/07-expenses.py
   :linenos:
   :lines: 57-82
   :emphasize-lines: 1, 23

Since these slots are methods, we can access the class variables, like our `QTableWidget` to
interact with it.

The mechanism to add elements into the table is described as the following:

  * get the *description* and *price* from the fields,
  * insert a new empty row to the table,
  * set the values for the empty row in each column,
  * clear the input text fields,
  * include the global count of table rows.

To exit the application you can use the `quit()` method of the unique `QApplication` instance, and
to clear the content of the table you can just set the table *row count*, and the internal count to
zero.

Verification step
-----------------

Adding information to the table needs to be a critical action that require a verification step
to avoid adding invalid information, for example, empty information.

You can use a signal from `QLineEdit` called *textChanged* which will be emitted every
time something inside changes, i.e.: each key stroke.

You can connect two different object's signal to the same slot, and this will be the case
for your current application:

.. literalinclude:: steps/08-expenses.py
   :linenos:
   :lines: 57-58

The content of the *check_disable* slot will be really simple:

.. literalinclude:: steps/08-expenses.py
   :linenos:
   :lines: 77-80

You have two options, write a verification based on the current value
of the string you retrieve, or manually get the whole content of both
`QLineEdit`. The second is preferred in this case, so you can verify
if the two inputs are not empty to enable the button *Add*.

.. note:: Qt also provides a special class called
          `QValidator <https://doc.qt.io/qtforpython/PySide6/QtGui/QValidator.html?highlight=qvalidator>`_
          that you can use to validate any input.

Empty chart view
----------------

New items can be added to the table, and the visualization is so far
OK, but you can accomplish more by representing the data graphically.

First you will include an empty `QChartView` placeholder into the right
side of your application.

.. literalinclude:: steps/09-expenses.py
   :linenos:
   :lines: 30-32

Additionally the order of how you include widgets to the right
`QVBoxLayout` will also change.

.. literalinclude:: steps/09-expenses.py
   :linenos:
   :lines: 46-54
   :emphasize-lines: 8

Notice that before we had a line with `self.right.addStretch()`
to fill up the vertical space between the *Add* and the *Clear* buttons,
but now, with the `QChartView` it will not be necessary.

Also, you need include a *Plot* button if you want to do it on-demand.

Full application
----------------

For the final step, you will need to connect the *Plot* button
to a slot that creates a chart and includes it into your `QChartView`.

.. literalinclude:: steps/10-expenses.py
   :linenos:
   :lines: 62-67
   :emphasize-lines: 3

That is nothing new, since you already did it for the other buttons,
but now take a look at how to create a chart and include it into
your `QChartView`.

.. literalinclude:: steps/10-expenses.py
   :linenos:
   :lines: 95-107

The following steps show how to fill a `QPieSeries`:

  * create a `QPieSeries`,
  * iterate over the table row IDs,
  * get the items at the *i* position,
  * add those values to the *series*.

Once the series has been populated with our data, you create a new `QChart`,
add the series on it, and optionally set an alignment for the legend.

The final line `self.chart_view.setChart(chart)` is in charge of bringing
your newly created chart to the `QChartView`.

The application will look like this:

.. image:: expenses_tool.png

And now you can see the whole code:

.. literalinclude:: main.py
   :linenos:
