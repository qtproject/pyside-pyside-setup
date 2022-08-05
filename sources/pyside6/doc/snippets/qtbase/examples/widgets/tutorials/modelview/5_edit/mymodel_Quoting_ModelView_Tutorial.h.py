from PySide6.QtCore import QAbstractTableModel

COLS = 3
ROWS = 2


class MyModel(QAbstractTableModel):

    editCompleted = Signal(str)

    def __init__(self, parent=None):
        ...

    def rowCount(self, parent=None):
        ...

    def columnCount(self, parent=None):
        ...

    def data(self, index, role=Qt.DisplayRole):
        ...

    def setData(self, index, value, role):
        ...

    def flags(self, index):
        ...
