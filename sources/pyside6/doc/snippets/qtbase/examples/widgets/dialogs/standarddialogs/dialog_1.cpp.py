d, ok = QInputDialog.getDouble(self, "QInputDialog::getDouble()",
                               "Amount:", 37.56, -10000, 10000, 2,
                               Qt.WindowFlags(), 1)
if ok:
   doubleLabel.setText(f"${d}")
