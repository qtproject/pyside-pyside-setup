# Copyright (C) 2013 Riverbank Computing Limited.
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the widgets/dialogs/trivialwizard example from Qt v5.x"""

import sys

from PySide6.QtWidgets import (QApplication, QFormLayout, QLabel, QLineEdit,
                               QVBoxLayout, QWizardPage, QWizard)


def create_intro_page():
    page = QWizardPage()
    page.setTitle("Introduction")

    label = QLabel("This wizard will help you register your copy of "
                   "Super Product Two.")
    label.setWordWrap(True)

    layout = QVBoxLayout(page)
    layout.addWidget(label)

    return page


def create_registration_page():
    page = QWizardPage()
    page.setTitle("Registration")
    page.setSubTitle("Please fill both fields.")

    layout = QFormLayout(page)
    layout.addRow("Name:", QLineEdit())
    layout.addRow("Email address:", QLineEdit())

    return page


def create_conclusion_page():
    page = QWizardPage()
    page.setTitle("Conclusion")

    label = QLabel("You are now successfully registered. Have a nice day!")
    label.setWordWrap(True)

    layout = QVBoxLayout(page)
    layout.addWidget(label)

    return page


if __name__ == '__main__':
    app = QApplication(sys.argv)

    wizard = QWizard()
    wizard.addPage(create_intro_page())
    wizard.addPage(create_registration_page())
    wizard.addPage(create_conclusion_page())

    wizard.setWindowTitle("Trivial Wizard")
    wizard.show()

    sys.exit(wizard.exec())
