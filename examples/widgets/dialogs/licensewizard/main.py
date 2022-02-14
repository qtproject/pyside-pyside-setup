# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import sys

from PySide6.QtWidgets import QApplication

from licensewizard import LicenseWizard

if __name__ == "__main__":
    app = QApplication(sys.argv)

    wizard = LicenseWizard()
    wizard.show()
    sys.exit(app.exec())
