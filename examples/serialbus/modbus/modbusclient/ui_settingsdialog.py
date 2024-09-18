# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settingsdialog.ui'
##
## Created by: Qt User Interface Compiler version 6.8.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QGridLayout,
    QGroupBox, QLabel, QPushButton, QSizePolicy,
    QSpacerItem, QSpinBox, QWidget)

class Ui_SettingsDialog(object):
    def setupUi(self, SettingsDialog):
        if not SettingsDialog.objectName():
            SettingsDialog.setObjectName(u"SettingsDialog")
        SettingsDialog.resize(259, 321)
        self.gridLayout = QGridLayout(SettingsDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalSpacer = QSpacerItem(20, 43, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 3, 1, 1, 1)

        self.timeoutSpinner = QSpinBox(SettingsDialog)
        self.timeoutSpinner.setObjectName(u"timeoutSpinner")
        self.timeoutSpinner.setAccelerated(True)
        self.timeoutSpinner.setMinimum(-1)
        self.timeoutSpinner.setMaximum(5000)
        self.timeoutSpinner.setSingleStep(20)
        self.timeoutSpinner.setValue(200)

        self.gridLayout.addWidget(self.timeoutSpinner, 1, 1, 1, 1)

        self.label = QLabel(SettingsDialog)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)

        self.applyButton = QPushButton(SettingsDialog)
        self.applyButton.setObjectName(u"applyButton")

        self.gridLayout.addWidget(self.applyButton, 4, 1, 1, 1)

        self.groupBox = QGroupBox(SettingsDialog)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_2 = QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_2.addWidget(self.label_2, 0, 0, 1, 1)

        self.parityCombo = QComboBox(self.groupBox)
        self.parityCombo.addItem("")
        self.parityCombo.addItem("")
        self.parityCombo.addItem("")
        self.parityCombo.addItem("")
        self.parityCombo.addItem("")
        self.parityCombo.setObjectName(u"parityCombo")

        self.gridLayout_2.addWidget(self.parityCombo, 0, 1, 1, 1)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_2.addWidget(self.label_3, 1, 0, 1, 1)

        self.baudCombo = QComboBox(self.groupBox)
        self.baudCombo.addItem("")
        self.baudCombo.addItem("")
        self.baudCombo.addItem("")
        self.baudCombo.addItem("")
        self.baudCombo.addItem("")
        self.baudCombo.addItem("")
        self.baudCombo.addItem("")
        self.baudCombo.addItem("")
        self.baudCombo.setObjectName(u"baudCombo")

        self.gridLayout_2.addWidget(self.baudCombo, 1, 1, 1, 1)

        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_2.addWidget(self.label_4, 2, 0, 1, 1)

        self.dataBitsCombo = QComboBox(self.groupBox)
        self.dataBitsCombo.addItem("")
        self.dataBitsCombo.addItem("")
        self.dataBitsCombo.addItem("")
        self.dataBitsCombo.addItem("")
        self.dataBitsCombo.setObjectName(u"dataBitsCombo")

        self.gridLayout_2.addWidget(self.dataBitsCombo, 2, 1, 1, 1)

        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_2.addWidget(self.label_5, 3, 0, 1, 1)

        self.stopBitsCombo = QComboBox(self.groupBox)
        self.stopBitsCombo.addItem("")
        self.stopBitsCombo.addItem("")
        self.stopBitsCombo.addItem("")
        self.stopBitsCombo.setObjectName(u"stopBitsCombo")

        self.gridLayout_2.addWidget(self.stopBitsCombo, 3, 1, 1, 1)


        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 2)

        self.label_6 = QLabel(SettingsDialog)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout.addWidget(self.label_6, 2, 0, 1, 1)

        self.retriesSpinner = QSpinBox(SettingsDialog)
        self.retriesSpinner.setObjectName(u"retriesSpinner")
        self.retriesSpinner.setValue(3)

        self.gridLayout.addWidget(self.retriesSpinner, 2, 1, 1, 1)


        self.retranslateUi(SettingsDialog)

        QMetaObject.connectSlotsByName(SettingsDialog)
    # setupUi

    def retranslateUi(self, SettingsDialog):
        SettingsDialog.setWindowTitle(QCoreApplication.translate("SettingsDialog", u"Modbus Settings", None))
        self.timeoutSpinner.setSuffix(QCoreApplication.translate("SettingsDialog", u" ms", None))
        self.label.setText(QCoreApplication.translate("SettingsDialog", u"Response Timeout:", None))
        self.applyButton.setText(QCoreApplication.translate("SettingsDialog", u"Apply", None))
        self.groupBox.setTitle(QCoreApplication.translate("SettingsDialog", u"Serial Parameters", None))
        self.label_2.setText(QCoreApplication.translate("SettingsDialog", u"Parity:", None))
        self.parityCombo.setItemText(0, QCoreApplication.translate("SettingsDialog", u"No", None))
        self.parityCombo.setItemText(1, QCoreApplication.translate("SettingsDialog", u"Even", None))
        self.parityCombo.setItemText(2, QCoreApplication.translate("SettingsDialog", u"Odd", None))
        self.parityCombo.setItemText(3, QCoreApplication.translate("SettingsDialog", u"Space", None))
        self.parityCombo.setItemText(4, QCoreApplication.translate("SettingsDialog", u"Mark", None))

        self.label_3.setText(QCoreApplication.translate("SettingsDialog", u"Baud Rate:", None))
        self.baudCombo.setItemText(0, QCoreApplication.translate("SettingsDialog", u"1200", None))
        self.baudCombo.setItemText(1, QCoreApplication.translate("SettingsDialog", u"2400", None))
        self.baudCombo.setItemText(2, QCoreApplication.translate("SettingsDialog", u"4800", None))
        self.baudCombo.setItemText(3, QCoreApplication.translate("SettingsDialog", u"9600", None))
        self.baudCombo.setItemText(4, QCoreApplication.translate("SettingsDialog", u"19200", None))
        self.baudCombo.setItemText(5, QCoreApplication.translate("SettingsDialog", u"38400", None))
        self.baudCombo.setItemText(6, QCoreApplication.translate("SettingsDialog", u"57600", None))
        self.baudCombo.setItemText(7, QCoreApplication.translate("SettingsDialog", u"115200", None))

        self.label_4.setText(QCoreApplication.translate("SettingsDialog", u"Data Bits:", None))
        self.dataBitsCombo.setItemText(0, QCoreApplication.translate("SettingsDialog", u"5", None))
        self.dataBitsCombo.setItemText(1, QCoreApplication.translate("SettingsDialog", u"6", None))
        self.dataBitsCombo.setItemText(2, QCoreApplication.translate("SettingsDialog", u"7", None))
        self.dataBitsCombo.setItemText(3, QCoreApplication.translate("SettingsDialog", u"8", None))

        self.label_5.setText(QCoreApplication.translate("SettingsDialog", u"Stop Bits:", None))
        self.stopBitsCombo.setItemText(0, QCoreApplication.translate("SettingsDialog", u"1", None))
        self.stopBitsCombo.setItemText(1, QCoreApplication.translate("SettingsDialog", u"3", None))
        self.stopBitsCombo.setItemText(2, QCoreApplication.translate("SettingsDialog", u"2", None))

        self.label_6.setText(QCoreApplication.translate("SettingsDialog", u"Number of retries:", None))
    # retranslateUi

