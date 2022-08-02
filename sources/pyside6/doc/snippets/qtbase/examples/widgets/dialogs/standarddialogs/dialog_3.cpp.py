text, ok = QInputDialog.getText(self, "QInputDialog.getText()",
                                "User name:", QLineEdit.Normal,
                                QDir.home().dirName())
if ok and text:
    textLabel.setText(text)
