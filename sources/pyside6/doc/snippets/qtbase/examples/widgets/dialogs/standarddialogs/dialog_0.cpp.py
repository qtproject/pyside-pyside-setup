i, ok = QInputDialog.getInt(self, "QInputDialog::getInt()",
                            "Percentage:", 25, 0, 100, 1)
if ok:
    integerLabel.setText(f"{i}")
