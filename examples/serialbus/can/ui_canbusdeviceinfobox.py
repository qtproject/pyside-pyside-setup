# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'canbusdeviceinfobox.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QGroupBox, QLabel,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_CanBusDeviceInfoBox(object):
    def setupUi(self, CanBusDeviceInfoBox):
        if not CanBusDeviceInfoBox.objectName():
            CanBusDeviceInfoBox.setObjectName(u"CanBusDeviceInfoBox")
        CanBusDeviceInfoBox.resize(319, 257)
        self.verticalLayout = QVBoxLayout(CanBusDeviceInfoBox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.pluginLabel = QLabel(CanBusDeviceInfoBox)
        self.pluginLabel.setObjectName(u"pluginLabel")

        self.verticalLayout.addWidget(self.pluginLabel)

        self.nameLabel = QLabel(CanBusDeviceInfoBox)
        self.nameLabel.setObjectName(u"nameLabel")

        self.verticalLayout.addWidget(self.nameLabel)

        self.descriptionLabel = QLabel(CanBusDeviceInfoBox)
        self.descriptionLabel.setObjectName(u"descriptionLabel")

        self.verticalLayout.addWidget(self.descriptionLabel)

        self.serialNumberLabel = QLabel(CanBusDeviceInfoBox)
        self.serialNumberLabel.setObjectName(u"serialNumberLabel")

        self.verticalLayout.addWidget(self.serialNumberLabel)

        self.aliasLabel = QLabel(CanBusDeviceInfoBox)
        self.aliasLabel.setObjectName(u"aliasLabel")

        self.verticalLayout.addWidget(self.aliasLabel)

        self.channelLabel = QLabel(CanBusDeviceInfoBox)
        self.channelLabel.setObjectName(u"channelLabel")

        self.verticalLayout.addWidget(self.channelLabel)

        self.isFlexibleDataRateCapable = QCheckBox(CanBusDeviceInfoBox)
        self.isFlexibleDataRateCapable.setObjectName(u"isFlexibleDataRateCapable")
        self.isFlexibleDataRateCapable.setEnabled(True)
        self.isFlexibleDataRateCapable.setCheckable(True)

        self.verticalLayout.addWidget(self.isFlexibleDataRateCapable)

        self.isVirtual = QCheckBox(CanBusDeviceInfoBox)
        self.isVirtual.setObjectName(u"isVirtual")
        self.isVirtual.setCheckable(True)

        self.verticalLayout.addWidget(self.isVirtual)


        self.retranslateUi(CanBusDeviceInfoBox)

        QMetaObject.connectSlotsByName(CanBusDeviceInfoBox)
    # setupUi

    def retranslateUi(self, CanBusDeviceInfoBox):
        CanBusDeviceInfoBox.setWindowTitle(QCoreApplication.translate("CanBusDeviceInfoBox", u"CAN Interface Properties", None))
        self.pluginLabel.setText("")
        self.nameLabel.setText("")
        self.descriptionLabel.setText("")
        self.serialNumberLabel.setText("")
        self.aliasLabel.setText("")
        self.channelLabel.setText("")
        self.isFlexibleDataRateCapable.setText(QCoreApplication.translate("CanBusDeviceInfoBox", u"Flexible Data Rate", None))
        self.isVirtual.setText(QCoreApplication.translate("CanBusDeviceInfoBox", u"Virtual", None))
    # retranslateUi

