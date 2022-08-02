items = ["Spring", "Summer", "Fall", "Winter"]
item, ok = QInputDialog.getItem(self, "QInputDialog::getItem()",
                                "Season:", items, 0, False)
if ok and item:
    itemLabel.setText(item)
