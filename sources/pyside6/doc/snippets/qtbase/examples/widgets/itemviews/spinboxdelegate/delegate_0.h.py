class SpinBoxDelegate(QStyledItemDelegate):
    """A delegate that allows the user to change integer values from the model
       using a spin box widget. """

    def __init__(self, parent=None):
        ...

    def createEditor(self, parent, option, index):
        ...

    def setEditorData(self, editor, index):
        ...

    def setModelData(self, editor, model, index):
        ...

    def updateEditorGeometry(self, editor, option, index):
        ...
