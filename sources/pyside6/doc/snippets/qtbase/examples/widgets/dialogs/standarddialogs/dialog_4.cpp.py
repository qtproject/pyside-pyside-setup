text, ok = QInputDialog.getMultiLineText(self, "QInputDialog.getMultiLineText()", ""
                                         "Address:", "John Doe\nFreedom Street")
if ok and text:
    multiLineTextLabel.setText(text)
