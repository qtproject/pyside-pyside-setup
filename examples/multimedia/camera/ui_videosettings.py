# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'videosettings.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QDialog,
    QDialogButtonBox, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QSizePolicy, QSlider, QSpacerItem,
    QSpinBox, QVBoxLayout, QWidget)

class Ui_VideoSettingsUi(object):
    def setupUi(self, VideoSettingsUi):
        if not VideoSettingsUi.objectName():
            VideoSettingsUi.setObjectName(u"VideoSettingsUi")
        VideoSettingsUi.resize(686, 499)
        self.gridLayout_3 = QGridLayout(VideoSettingsUi)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.buttonBox = QDialogButtonBox(VideoSettingsUi)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.gridLayout_3.addWidget(self.buttonBox, 4, 1, 1, 1)

        self.groupBox_2 = QGroupBox(VideoSettingsUi)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.gridLayout_2 = QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_8 = QLabel(self.groupBox_2)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout_2.addWidget(self.label_8, 0, 0, 1, 2)

        self.videoCodecBox = QComboBox(self.groupBox_2)
        self.videoCodecBox.setObjectName(u"videoCodecBox")

        self.gridLayout_2.addWidget(self.videoCodecBox, 5, 0, 1, 2)

        self.label_9 = QLabel(self.groupBox_2)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout_2.addWidget(self.label_9, 2, 0, 1, 2)

        self.label_6 = QLabel(self.groupBox_2)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout_2.addWidget(self.label_6, 4, 0, 1, 2)

        self.videoFormatBox = QComboBox(self.groupBox_2)
        self.videoFormatBox.setObjectName(u"videoFormatBox")

        self.gridLayout_2.addWidget(self.videoFormatBox, 1, 0, 1, 2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.fpsSpinBox = QSpinBox(self.groupBox_2)
        self.fpsSpinBox.setObjectName(u"fpsSpinBox")

        self.horizontalLayout.addWidget(self.fpsSpinBox)

        self.fpsSlider = QSlider(self.groupBox_2)
        self.fpsSlider.setObjectName(u"fpsSlider")
        self.fpsSlider.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout.addWidget(self.fpsSlider)


        self.gridLayout_2.addLayout(self.horizontalLayout, 3, 0, 1, 2)


        self.gridLayout_3.addWidget(self.groupBox_2, 2, 1, 1, 1)

        self.widget = QWidget(VideoSettingsUi)
        self.widget.setObjectName(u"widget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.verticalLayout_3 = QVBoxLayout(self.widget)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.groupBox_3 = QGroupBox(self.widget)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label_2 = QLabel(self.groupBox_3)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout_2.addWidget(self.label_2)

        self.audioCodecBox = QComboBox(self.groupBox_3)
        self.audioCodecBox.setObjectName(u"audioCodecBox")

        self.verticalLayout_2.addWidget(self.audioCodecBox)

        self.label_5 = QLabel(self.groupBox_3)
        self.label_5.setObjectName(u"label_5")

        self.verticalLayout_2.addWidget(self.label_5)

        self.audioSampleRateBox = QSpinBox(self.groupBox_3)
        self.audioSampleRateBox.setObjectName(u"audioSampleRateBox")

        self.verticalLayout_2.addWidget(self.audioSampleRateBox)


        self.verticalLayout_3.addWidget(self.groupBox_3)

        self.groupBox = QGroupBox(self.widget)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.verticalLayout.addWidget(self.label_3)

        self.qualitySlider = QSlider(self.groupBox)
        self.qualitySlider.setObjectName(u"qualitySlider")
        self.qualitySlider.setMaximum(4)
        self.qualitySlider.setOrientation(Qt.Orientation.Horizontal)

        self.verticalLayout.addWidget(self.qualitySlider)

        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")

        self.verticalLayout.addWidget(self.label_4)

        self.containerFormatBox = QComboBox(self.groupBox)
        self.containerFormatBox.setObjectName(u"containerFormatBox")

        self.verticalLayout.addWidget(self.containerFormatBox)


        self.verticalLayout_3.addWidget(self.groupBox)


        self.gridLayout_3.addWidget(self.widget, 2, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer, 3, 0, 1, 1)


        self.retranslateUi(VideoSettingsUi)
        self.buttonBox.accepted.connect(VideoSettingsUi.accept)
        self.buttonBox.rejected.connect(VideoSettingsUi.reject)

        QMetaObject.connectSlotsByName(VideoSettingsUi)
    # setupUi

    def retranslateUi(self, VideoSettingsUi):
        VideoSettingsUi.setWindowTitle(QCoreApplication.translate("VideoSettingsUi", u"Video Settings", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("VideoSettingsUi", u"Video", None))
        self.label_8.setText(QCoreApplication.translate("VideoSettingsUi", u"Camera Format", None))
        self.label_9.setText(QCoreApplication.translate("VideoSettingsUi", u"Framerate:", None))
        self.label_6.setText(QCoreApplication.translate("VideoSettingsUi", u"Video Codec:", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("VideoSettingsUi", u"Audio", None))
        self.label_2.setText(QCoreApplication.translate("VideoSettingsUi", u"Audio Codec:", None))
        self.label_5.setText(QCoreApplication.translate("VideoSettingsUi", u"Sample Rate:", None))
        self.label_3.setText(QCoreApplication.translate("VideoSettingsUi", u"Quality:", None))
        self.label_4.setText(QCoreApplication.translate("VideoSettingsUi", u"File Format:", None))
    # retranslateUi

