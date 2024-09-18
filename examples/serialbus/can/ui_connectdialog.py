# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'connectdialog.ui'
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
from PySide6.QtWidgets import (QAbstractSpinBox, QApplication, QCheckBox, QComboBox,
    QDialog, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QSpinBox, QVBoxLayout, QWidget)

from bitratebox import BitRateBox
from canbusdeviceinfobox import CanBusDeviceInfoBox

class Ui_ConnectDialog(object):
    def setupUi(self, ConnectDialog):
        if not ConnectDialog.objectName():
            ConnectDialog.setObjectName(u"ConnectDialog")
        ConnectDialog.resize(542, 558)
        self.gridLayout_6 = QGridLayout(ConnectDialog)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.gridLayout_5 = QGridLayout()
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.selectPluginBox = QGroupBox(ConnectDialog)
        self.selectPluginBox.setObjectName(u"selectPluginBox")
        self.gridLayout = QGridLayout(self.selectPluginBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.pluginListBox = QComboBox(self.selectPluginBox)
        self.pluginListBox.setObjectName(u"pluginListBox")

        self.gridLayout.addWidget(self.pluginListBox, 0, 0, 1, 1)


        self.gridLayout_5.addWidget(self.selectPluginBox, 0, 0, 1, 1)

        self.groupBox = QGroupBox(ConnectDialog)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_2 = QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.ringBufferBox = QCheckBox(self.groupBox)
        self.ringBufferBox.setObjectName(u"ringBufferBox")
        self.ringBufferBox.setChecked(True)

        self.horizontalLayout_2.addWidget(self.ringBufferBox)

        self.ringBufferLimitBox = QSpinBox(self.groupBox)
        self.ringBufferLimitBox.setObjectName(u"ringBufferLimitBox")
        self.ringBufferLimitBox.setMinimum(10)
        self.ringBufferLimitBox.setMaximum(10000000)
        self.ringBufferLimitBox.setSingleStep(10)
        self.ringBufferLimitBox.setStepType(QAbstractSpinBox.StepType.AdaptiveDecimalStepType)
        self.ringBufferLimitBox.setValue(1000)

        self.horizontalLayout_2.addWidget(self.ringBufferLimitBox)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.autoscrollBox = QCheckBox(self.groupBox)
        self.autoscrollBox.setObjectName(u"autoscrollBox")

        self.verticalLayout_2.addWidget(self.autoscrollBox)


        self.gridLayout_2.addLayout(self.verticalLayout_2, 0, 0, 1, 1)


        self.gridLayout_5.addWidget(self.groupBox, 4, 0, 1, 2)

        self.useConfigurationBox = QCheckBox(ConnectDialog)
        self.useConfigurationBox.setObjectName(u"useConfigurationBox")

        self.gridLayout_5.addWidget(self.useConfigurationBox, 3, 0, 1, 1)

        self.configurationBox = QGroupBox(ConnectDialog)
        self.configurationBox.setObjectName(u"configurationBox")
        self.configurationBox.setEnabled(False)
        self.gridLayout_4 = QGridLayout(self.configurationBox)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.rawFilterLabel = QLabel(self.configurationBox)
        self.rawFilterLabel.setObjectName(u"rawFilterLabel")

        self.gridLayout_4.addWidget(self.rawFilterLabel, 0, 0, 1, 1)

        self.rawFilterEdit = QLineEdit(self.configurationBox)
        self.rawFilterEdit.setObjectName(u"rawFilterEdit")
        self.rawFilterEdit.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_4.addWidget(self.rawFilterEdit, 0, 1, 1, 1)

        self.errorFilterLabel = QLabel(self.configurationBox)
        self.errorFilterLabel.setObjectName(u"errorFilterLabel")

        self.gridLayout_4.addWidget(self.errorFilterLabel, 1, 0, 1, 1)

        self.errorFilterEdit = QLineEdit(self.configurationBox)
        self.errorFilterEdit.setObjectName(u"errorFilterEdit")
        self.errorFilterEdit.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_4.addWidget(self.errorFilterEdit, 1, 1, 1, 1)

        self.loopbackLabel = QLabel(self.configurationBox)
        self.loopbackLabel.setObjectName(u"loopbackLabel")

        self.gridLayout_4.addWidget(self.loopbackLabel, 2, 0, 1, 1)

        self.loopbackBox = QComboBox(self.configurationBox)
        self.loopbackBox.setObjectName(u"loopbackBox")

        self.gridLayout_4.addWidget(self.loopbackBox, 2, 1, 1, 1)

        self.receiveOwnLabel = QLabel(self.configurationBox)
        self.receiveOwnLabel.setObjectName(u"receiveOwnLabel")

        self.gridLayout_4.addWidget(self.receiveOwnLabel, 3, 0, 1, 1)

        self.receiveOwnBox = QComboBox(self.configurationBox)
        self.receiveOwnBox.setObjectName(u"receiveOwnBox")

        self.gridLayout_4.addWidget(self.receiveOwnBox, 3, 1, 1, 1)

        self.bitrateLabel = QLabel(self.configurationBox)
        self.bitrateLabel.setObjectName(u"bitrateLabel")

        self.gridLayout_4.addWidget(self.bitrateLabel, 4, 0, 1, 1)

        self.bitrateBox = BitRateBox(self.configurationBox)
        self.bitrateBox.setObjectName(u"bitrateBox")

        self.gridLayout_4.addWidget(self.bitrateBox, 4, 1, 1, 1)

        self.canFdLabel = QLabel(self.configurationBox)
        self.canFdLabel.setObjectName(u"canFdLabel")

        self.gridLayout_4.addWidget(self.canFdLabel, 5, 0, 1, 1)

        self.canFdBox = QComboBox(self.configurationBox)
        self.canFdBox.setObjectName(u"canFdBox")

        self.gridLayout_4.addWidget(self.canFdBox, 5, 1, 1, 1)

        self.dataBitrateLabel = QLabel(self.configurationBox)
        self.dataBitrateLabel.setObjectName(u"dataBitrateLabel")

        self.gridLayout_4.addWidget(self.dataBitrateLabel, 6, 0, 1, 1)

        self.dataBitrateBox = BitRateBox(self.configurationBox)
        self.dataBitrateBox.setObjectName(u"dataBitrateBox")

        self.gridLayout_4.addWidget(self.dataBitrateBox, 6, 1, 1, 1)


        self.gridLayout_5.addWidget(self.configurationBox, 0, 1, 4, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(96, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.cancelButton = QPushButton(ConnectDialog)
        self.cancelButton.setObjectName(u"cancelButton")
        self.cancelButton.setAutoDefault(False)

        self.horizontalLayout.addWidget(self.cancelButton)

        self.okButton = QPushButton(ConnectDialog)
        self.okButton.setObjectName(u"okButton")
        self.okButton.setAutoDefault(False)

        self.horizontalLayout.addWidget(self.okButton)


        self.gridLayout_5.addLayout(self.horizontalLayout, 5, 0, 1, 2)

        self.specifyInterfaceNameBox = QGroupBox(ConnectDialog)
        self.specifyInterfaceNameBox.setObjectName(u"specifyInterfaceNameBox")
        self.gridLayout_3 = QGridLayout(self.specifyInterfaceNameBox)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.interfaceListBox = QComboBox(self.specifyInterfaceNameBox)
        self.interfaceListBox.setObjectName(u"interfaceListBox")
        self.interfaceListBox.setEditable(True)

        self.gridLayout_3.addWidget(self.interfaceListBox, 0, 0, 1, 1)


        self.gridLayout_5.addWidget(self.specifyInterfaceNameBox, 1, 0, 1, 1)

        self.deviceInfoBox = CanBusDeviceInfoBox(ConnectDialog)
        self.deviceInfoBox.setObjectName(u"deviceInfoBox")
        self.deviceInfoBox.setEnabled(True)

        self.gridLayout_5.addWidget(self.deviceInfoBox, 2, 0, 1, 1)


        self.gridLayout_6.addLayout(self.gridLayout_5, 0, 0, 1, 1)


        self.retranslateUi(ConnectDialog)

        self.okButton.setDefault(True)


        QMetaObject.connectSlotsByName(ConnectDialog)
    # setupUi

    def retranslateUi(self, ConnectDialog):
        ConnectDialog.setWindowTitle(QCoreApplication.translate("ConnectDialog", u"Connect", None))
        self.selectPluginBox.setTitle(QCoreApplication.translate("ConnectDialog", u"Select CAN plugin", None))
        self.groupBox.setTitle(QCoreApplication.translate("ConnectDialog", u"GUI Settings", None))
#if QT_CONFIG(tooltip)
        self.ringBufferBox.setToolTip(QCoreApplication.translate("ConnectDialog", u"<html><head/><body><p>Use ring buffer in table view model</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.ringBufferBox.setText(QCoreApplication.translate("ConnectDialog", u"Use ring buffer", None))
#if QT_CONFIG(tooltip)
        self.ringBufferLimitBox.setToolTip(QCoreApplication.translate("ConnectDialog", u"<html><head/><body><p>Limit of ring buffer in table view model</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.autoscrollBox.setToolTip(QCoreApplication.translate("ConnectDialog", u"<html><head/><body><p>Scroll to bottom table view on each portion of received frames</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.autoscrollBox.setText(QCoreApplication.translate("ConnectDialog", u"Autoscroll", None))
        self.useConfigurationBox.setText(QCoreApplication.translate("ConnectDialog", u"Custom configuration", None))
        self.configurationBox.setTitle(QCoreApplication.translate("ConnectDialog", u"Specify Configuration", None))
        self.rawFilterLabel.setText(QCoreApplication.translate("ConnectDialog", u"RAW Filter", None))
        self.errorFilterLabel.setText(QCoreApplication.translate("ConnectDialog", u"Error Filter", None))
        self.errorFilterEdit.setPlaceholderText(QCoreApplication.translate("ConnectDialog", u"FrameError bits", None))
        self.loopbackLabel.setText(QCoreApplication.translate("ConnectDialog", u"Loopback", None))
        self.receiveOwnLabel.setText(QCoreApplication.translate("ConnectDialog", u"Receive Own", None))
        self.bitrateLabel.setText(QCoreApplication.translate("ConnectDialog", u"Bitrate", None))
        self.canFdLabel.setText(QCoreApplication.translate("ConnectDialog", u"CAN FD", None))
        self.dataBitrateLabel.setText(QCoreApplication.translate("ConnectDialog", u"Data Bitrate", None))
        self.cancelButton.setText(QCoreApplication.translate("ConnectDialog", u"Cancel", None))
        self.okButton.setText(QCoreApplication.translate("ConnectDialog", u"OK", None))
        self.specifyInterfaceNameBox.setTitle(QCoreApplication.translate("ConnectDialog", u"Specify CAN interface name", None))
        self.deviceInfoBox.setTitle(QCoreApplication.translate("ConnectDialog", u"CAN Interface Properties", None))
    # retranslateUi

