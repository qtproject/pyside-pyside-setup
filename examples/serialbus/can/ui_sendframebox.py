# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'sendframebox.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QGroupBox, QHBoxLayout,
    QLabel, QLayout, QLineEdit, QPushButton,
    QRadioButton, QSizePolicy, QVBoxLayout, QWidget)

class Ui_SendFrameBox(object):
    def setupUi(self, SendFrameBox):
        if not SendFrameBox.objectName():
            SendFrameBox.setObjectName(u"SendFrameBox")
        SendFrameBox.resize(505, 219)
        self.verticalLayout_4 = QVBoxLayout(SendFrameBox)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.frameTypeBox = QGroupBox(SendFrameBox)
        self.frameTypeBox.setObjectName(u"frameTypeBox")
        self.frameTypeBox.setCheckable(False)
        self.horizontalLayout = QHBoxLayout(self.frameTypeBox)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, 0, -1, 0)
        self.dataFrame = QRadioButton(self.frameTypeBox)
        self.dataFrame.setObjectName(u"dataFrame")
        self.dataFrame.setChecked(True)

        self.horizontalLayout.addWidget(self.dataFrame)

        self.remoteFrame = QRadioButton(self.frameTypeBox)
        self.remoteFrame.setObjectName(u"remoteFrame")

        self.horizontalLayout.addWidget(self.remoteFrame)

        self.errorFrame = QRadioButton(self.frameTypeBox)
        self.errorFrame.setObjectName(u"errorFrame")

        self.horizontalLayout.addWidget(self.errorFrame)


        self.verticalLayout_4.addWidget(self.frameTypeBox)

        self.frameOptionsBox = QGroupBox(SendFrameBox)
        self.frameOptionsBox.setObjectName(u"frameOptionsBox")
        self.horizontalLayout_2 = QHBoxLayout(self.frameOptionsBox)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(-1, 0, -1, 0)
        self.extendedFormatBox = QCheckBox(self.frameOptionsBox)
        self.extendedFormatBox.setObjectName(u"extendedFormatBox")

        self.horizontalLayout_2.addWidget(self.extendedFormatBox)

        self.flexibleDataRateBox = QCheckBox(self.frameOptionsBox)
        self.flexibleDataRateBox.setObjectName(u"flexibleDataRateBox")

        self.horizontalLayout_2.addWidget(self.flexibleDataRateBox)

        self.bitrateSwitchBox = QCheckBox(self.frameOptionsBox)
        self.bitrateSwitchBox.setObjectName(u"bitrateSwitchBox")
        self.bitrateSwitchBox.setEnabled(False)

        self.horizontalLayout_2.addWidget(self.bitrateSwitchBox)


        self.verticalLayout_4.addWidget(self.frameOptionsBox)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frameIdLabel = QLabel(SendFrameBox)
        self.frameIdLabel.setObjectName(u"frameIdLabel")

        self.verticalLayout.addWidget(self.frameIdLabel)

        self.frameIdEdit = QLineEdit(SendFrameBox)
        self.frameIdEdit.setObjectName(u"frameIdEdit")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frameIdEdit.sizePolicy().hasHeightForWidth())
        self.frameIdEdit.setSizePolicy(sizePolicy)
        self.frameIdEdit.setClearButtonEnabled(True)

        self.verticalLayout.addWidget(self.frameIdEdit)


        self.horizontalLayout_3.addLayout(self.verticalLayout)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.payloadLabel = QLabel(SendFrameBox)
        self.payloadLabel.setObjectName(u"payloadLabel")

        self.verticalLayout_2.addWidget(self.payloadLabel)

        self.payloadEdit = QLineEdit(SendFrameBox)
        self.payloadEdit.setObjectName(u"payloadEdit")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(2)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.payloadEdit.sizePolicy().hasHeightForWidth())
        self.payloadEdit.setSizePolicy(sizePolicy1)
        self.payloadEdit.setClearButtonEnabled(True)

        self.verticalLayout_2.addWidget(self.payloadEdit)


        self.horizontalLayout_3.addLayout(self.verticalLayout_2)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.label = QLabel(SendFrameBox)
        self.label.setObjectName(u"label")

        self.verticalLayout_3.addWidget(self.label)

        self.sendButton = QPushButton(SendFrameBox)
        self.sendButton.setObjectName(u"sendButton")

        self.verticalLayout_3.addWidget(self.sendButton)


        self.horizontalLayout_3.addLayout(self.verticalLayout_3)


        self.verticalLayout_4.addLayout(self.horizontalLayout_3)

#if QT_CONFIG(shortcut)
        self.frameIdLabel.setBuddy(self.frameIdEdit)
        self.payloadLabel.setBuddy(self.payloadEdit)
#endif // QT_CONFIG(shortcut)

        self.retranslateUi(SendFrameBox)

        QMetaObject.connectSlotsByName(SendFrameBox)
    # setupUi

    def retranslateUi(self, SendFrameBox):
        SendFrameBox.setWindowTitle(QCoreApplication.translate("SendFrameBox", u"Dialog", None))
        SendFrameBox.setTitle("")
        self.frameTypeBox.setTitle(QCoreApplication.translate("SendFrameBox", u"Frame Type", None))
#if QT_CONFIG(tooltip)
        self.dataFrame.setToolTip(QCoreApplication.translate("SendFrameBox", u"Sends a CAN data frame.", None))
#endif // QT_CONFIG(tooltip)
        self.dataFrame.setText(QCoreApplication.translate("SendFrameBox", u"D&ata Frame", None))
#if QT_CONFIG(tooltip)
        self.remoteFrame.setToolTip(QCoreApplication.translate("SendFrameBox", u"Sends a CAN remote request frame.", None))
#endif // QT_CONFIG(tooltip)
        self.remoteFrame.setText(QCoreApplication.translate("SendFrameBox", u"Re&mote Request Frame", None))
#if QT_CONFIG(tooltip)
        self.errorFrame.setToolTip(QCoreApplication.translate("SendFrameBox", u"Sends an error frame.", None))
#endif // QT_CONFIG(tooltip)
        self.errorFrame.setText(QCoreApplication.translate("SendFrameBox", u"&Error Frame", None))
        self.frameOptionsBox.setTitle(QCoreApplication.translate("SendFrameBox", u"Frame Options", None))
#if QT_CONFIG(tooltip)
        self.extendedFormatBox.setToolTip(QCoreApplication.translate("SendFrameBox", u"Allows extended frames with 29 bit identifier.", None))
#endif // QT_CONFIG(tooltip)
        self.extendedFormatBox.setText(QCoreApplication.translate("SendFrameBox", u"E&xtended Format", None))
#if QT_CONFIG(tooltip)
        self.flexibleDataRateBox.setToolTip(QCoreApplication.translate("SendFrameBox", u"Allows up to 64 byte payload data.", None))
#endif // QT_CONFIG(tooltip)
        self.flexibleDataRateBox.setText(QCoreApplication.translate("SendFrameBox", u"&Flexible Data-Rate", None))
#if QT_CONFIG(tooltip)
        self.bitrateSwitchBox.setToolTip(QCoreApplication.translate("SendFrameBox", u"Sends payload at higher data rate.", None))
#endif // QT_CONFIG(tooltip)
        self.bitrateSwitchBox.setText(QCoreApplication.translate("SendFrameBox", u"&Bitrate Switch", None))
        self.frameIdLabel.setText(QCoreApplication.translate("SendFrameBox", u"Frame &ID (hex)", None))
        self.frameIdEdit.setPlaceholderText(QCoreApplication.translate("SendFrameBox", u"123", None))
        self.payloadLabel.setText(QCoreApplication.translate("SendFrameBox", u"&Payload (hex)", None))
        self.payloadEdit.setPlaceholderText(QCoreApplication.translate("SendFrameBox", u"12 34 AB CE", None))
        self.label.setText("")
        self.sendButton.setText(QCoreApplication.translate("SendFrameBox", u"&Send", None))
    # retranslateUi

