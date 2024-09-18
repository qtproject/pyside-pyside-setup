# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'device.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QDialog, QGroupBox,
    QHBoxLayout, QListWidget, QListWidgetItem, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_DeviceDiscovery(object):
    def setupUi(self, DeviceDiscovery):
        if not DeviceDiscovery.objectName():
            DeviceDiscovery.setObjectName(u"DeviceDiscovery")
        DeviceDiscovery.resize(400, 411)
        self.verticalLayout = QVBoxLayout(DeviceDiscovery)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.list = QListWidget(DeviceDiscovery)
        self.list.setObjectName(u"list")

        self.verticalLayout.addWidget(self.list)

        self.groupBox = QGroupBox(DeviceDiscovery)
        self.groupBox.setObjectName(u"groupBox")
        self.horizontalLayout_2 = QHBoxLayout(self.groupBox)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.power = QCheckBox(self.groupBox)
        self.power.setObjectName(u"power")
        self.power.setChecked(True)

        self.horizontalLayout_2.addWidget(self.power)

        self.discoverable = QCheckBox(self.groupBox)
        self.discoverable.setObjectName(u"discoverable")
        self.discoverable.setChecked(True)

        self.horizontalLayout_2.addWidget(self.discoverable)


        self.verticalLayout.addWidget(self.groupBox)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.scan = QPushButton(DeviceDiscovery)
        self.scan.setObjectName(u"scan")

        self.horizontalLayout.addWidget(self.scan)

        self.clear = QPushButton(DeviceDiscovery)
        self.clear.setObjectName(u"clear")

        self.horizontalLayout.addWidget(self.clear)

        self.quit = QPushButton(DeviceDiscovery)
        self.quit.setObjectName(u"quit")

        self.horizontalLayout.addWidget(self.quit)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(DeviceDiscovery)
        self.quit.clicked.connect(DeviceDiscovery.accept)
        self.clear.clicked.connect(self.list.clear)

        QMetaObject.connectSlotsByName(DeviceDiscovery)
    # setupUi

    def retranslateUi(self, DeviceDiscovery):
        DeviceDiscovery.setWindowTitle(QCoreApplication.translate("DeviceDiscovery", u"Bluetooth Scanner", None))
        self.groupBox.setTitle(QCoreApplication.translate("DeviceDiscovery", u"Local Device", None))
        self.power.setText(QCoreApplication.translate("DeviceDiscovery", u"Bluetooth Powered On", None))
        self.discoverable.setText(QCoreApplication.translate("DeviceDiscovery", u"Discoverable", None))
        self.scan.setText(QCoreApplication.translate("DeviceDiscovery", u"Scan", None))
        self.clear.setText(QCoreApplication.translate("DeviceDiscovery", u"Clear", None))
        self.quit.setText(QCoreApplication.translate("DeviceDiscovery", u"Quit", None))
    # retranslateUi

