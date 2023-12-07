Registers a Python created custom widget to QUiLoader, so it can be recognized
when loading a `.ui` file. The custom widget type is passed via the
``customWidgetType`` argument. This is needed when you want to override a
virtual method of some widget in the interface, since duck punching will not
work with widgets created by QUiLoader based on the contents of the `.ui` file.

(Remember that
`duck punching virtual methods is an invitation for your own demise! <https://doc.qt.io/qtforpython/shiboken6/wordsofadvice.html#duck-punching-and-virtual-methods>`_)

Let's see an obvious example. If you want to create a new widget it's probable you'll end up
overriding :class:`~PySide6.QtGui.QWidget`'s :meth:`~PySide6.QtGui.QWidget.paintEvent` method.

.. code-block:: python

   class Circle(QWidget):
       def paintEvent(self, event):
           with QPainter(self) as painter:
               painter.setPen(self.pen)
               painter.setBrush(QBrush(self.color))
               painter.drawEllipse(event.rect().center(), 20, 20)

   # ...

   loader = QUiLoader()
   loader.registerCustomWidget(Circle)
   circle = loader.load('circle.ui')
   circle.show()

   # ...
