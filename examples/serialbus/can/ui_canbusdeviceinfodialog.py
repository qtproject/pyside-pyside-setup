# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'canbusdeviceinfodialog.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

from canbusdeviceinfobox import CanBusDeviceInfoBox

class Ui_CanBusDeviceInfoDialog(object):
    def setupUi(self, CanBusDeviceInfoDialog):
        if not CanBusDeviceInfoDialog.objectName():
            CanBusDeviceInfoDialog.setObjectName(u"CanBusDeviceInfoDialog")
        CanBusDeviceInfoDialog.resize(237, 225)
        self.verticalLayout = QVBoxLayout(CanBusDeviceInfoDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.deviceInfoBox = CanBusDeviceInfoBox(CanBusDeviceInfoDialog)
        self.deviceInfoBox.setObjectName(u"deviceInfoBox")
        self.deviceInfoBox.setEnabled(True)

        self.verticalLayout.addWidget(self.deviceInfoBox)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.okButton = QPushButton(CanBusDeviceInfoDialog)
        self.okButton.setObjectName(u"okButton")

        self.horizontalLayout.addWidget(self.okButton)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(CanBusDeviceInfoDialog)

        self.okButton.setDefault(True)


        QMetaObject.connectSlotsByName(CanBusDeviceInfoDialog)
    # setupUi

    def retranslateUi(self, CanBusDeviceInfoDialog):
        CanBusDeviceInfoDialog.setWindowTitle(QCoreApplication.translate("CanBusDeviceInfoDialog", u"CAN Interface Properties", None))
        self.deviceInfoBox.setTitle(QCoreApplication.translate("CanBusDeviceInfoDialog", u"CAN Interface Properties", None))
        self.okButton.setText(QCoreApplication.translate("CanBusDeviceInfoDialog", u"Ok", None))
    # retranslateUi

