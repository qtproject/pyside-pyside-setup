from PySide6.QtCore import QAbstractTableModel

class MyModel(QAbstractTableModel):

   def __init__(self, parent = None):
       ...

   def rowCount(self, parent = None):
       ...

   def columnCount(self, parent = None):
       ...

   def data(self, index, role = Qt.DisplayRole):
       ...
