# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'imagesettings.ui'
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
    QDialogButtonBox, QGridLayout, QGroupBox, QLabel,
    QSizePolicy, QSlider, QSpacerItem, QWidget)

class Ui_ImageSettingsUi(object):
    def setupUi(self, ImageSettingsUi):
        if not ImageSettingsUi.objectName():
            ImageSettingsUi.setObjectName(u"ImageSettingsUi")
        ImageSettingsUi.resize(332, 270)
        self.gridLayout = QGridLayout(ImageSettingsUi)
        self.gridLayout.setObjectName(u"gridLayout")
        self.groupBox_2 = QGroupBox(ImageSettingsUi)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.gridLayout_2 = QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_8 = QLabel(self.groupBox_2)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout_2.addWidget(self.label_8, 0, 0, 1, 2)

        self.imageResolutionBox = QComboBox(self.groupBox_2)
        self.imageResolutionBox.setObjectName(u"imageResolutionBox")

        self.gridLayout_2.addWidget(self.imageResolutionBox, 1, 0, 1, 2)

        self.label_6 = QLabel(self.groupBox_2)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout_2.addWidget(self.label_6, 2, 0, 1, 2)

        self.imageCodecBox = QComboBox(self.groupBox_2)
        self.imageCodecBox.setObjectName(u"imageCodecBox")

        self.gridLayout_2.addWidget(self.imageCodecBox, 3, 0, 1, 2)

        self.label_7 = QLabel(self.groupBox_2)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout_2.addWidget(self.label_7, 4, 0, 1, 1)

        self.imageQualitySlider = QSlider(self.groupBox_2)
        self.imageQualitySlider.setObjectName(u"imageQualitySlider")
        self.imageQualitySlider.setMaximum(4)
        self.imageQualitySlider.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout_2.addWidget(self.imageQualitySlider, 4, 1, 1, 1)


        self.gridLayout.addWidget(self.groupBox_2, 0, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 14, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 1, 0, 1, 1)

        self.buttonBox = QDialogButtonBox(ImageSettingsUi)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)


        self.retranslateUi(ImageSettingsUi)
        self.buttonBox.accepted.connect(ImageSettingsUi.accept)
        self.buttonBox.rejected.connect(ImageSettingsUi.reject)

        QMetaObject.connectSlotsByName(ImageSettingsUi)
    # setupUi

    def retranslateUi(self, ImageSettingsUi):
        ImageSettingsUi.setWindowTitle(QCoreApplication.translate("ImageSettingsUi", u"Image Settings", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("ImageSettingsUi", u"Image", None))
        self.label_8.setText(QCoreApplication.translate("ImageSettingsUi", u"Resolution:", None))
        self.label_6.setText(QCoreApplication.translate("ImageSettingsUi", u"Image Format:", None))
        self.label_7.setText(QCoreApplication.translate("ImageSettingsUi", u"Quality:", None))
    # retranslateUi

