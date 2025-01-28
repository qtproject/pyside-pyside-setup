# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'webauthdialog.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QGroupBox, QLabel, QLayout, QLineEdit,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_WebAuthDialog(object):
    def setupUi(self, WebAuthDialog):
        if not WebAuthDialog.objectName():
            WebAuthDialog.setObjectName(u"WebAuthDialog")
        WebAuthDialog.resize(563, 397)
        self.buttonBox = QDialogButtonBox(WebAuthDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(20, 320, 471, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok|QDialogButtonBox.Retry)
        self.m_headingLabel = QLabel(WebAuthDialog)
        self.m_headingLabel.setObjectName(u"m_headingLabel")
        self.m_headingLabel.setGeometry(QRect(30, 20, 321, 16))
        self.m_headingLabel.setWordWrap(False)
        self.m_description = QLabel(WebAuthDialog)
        self.m_description.setObjectName(u"m_description")
        self.m_description.setGeometry(QRect(30, 60, 491, 31))
        self.m_description.setWordWrap(False)
        self.layoutWidget = QWidget(WebAuthDialog)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(20, 100, 471, 171))
        self.m_mainVerticalLayout = QVBoxLayout(self.layoutWidget)
        self.m_mainVerticalLayout.setObjectName(u"m_mainVerticalLayout")
        self.m_mainVerticalLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.m_mainVerticalLayout.setContentsMargins(0, 0, 0, 0)
        self.m_pinGroupBox = QGroupBox(self.layoutWidget)
        self.m_pinGroupBox.setObjectName(u"m_pinGroupBox")
        self.m_pinGroupBox.setFlat(True)
        self.m_pinLabel = QLabel(self.m_pinGroupBox)
        self.m_pinLabel.setObjectName(u"m_pinLabel")
        self.m_pinLabel.setGeometry(QRect(10, 20, 58, 16))
        self.m_pinLineEdit = QLineEdit(self.m_pinGroupBox)
        self.m_pinLineEdit.setObjectName(u"m_pinLineEdit")
        self.m_pinLineEdit.setGeometry(QRect(90, 20, 113, 21))
        self.m_confirmPinLabel = QLabel(self.m_pinGroupBox)
        self.m_confirmPinLabel.setObjectName(u"m_confirmPinLabel")
        self.m_confirmPinLabel.setGeometry(QRect(10, 50, 81, 16))
        self.m_confirmPinLineEdit = QLineEdit(self.m_pinGroupBox)
        self.m_confirmPinLineEdit.setObjectName(u"m_confirmPinLineEdit")
        self.m_confirmPinLineEdit.setGeometry(QRect(90, 50, 113, 21))
        self.m_pinEntryErrorLabel = QLabel(self.m_pinGroupBox)
        self.m_pinEntryErrorLabel.setObjectName(u"m_pinEntryErrorLabel")
        self.m_pinEntryErrorLabel.setGeometry(QRect(10, 80, 441, 16))

        self.m_mainVerticalLayout.addWidget(self.m_pinGroupBox)


        self.retranslateUi(WebAuthDialog)

        QMetaObject.connectSlotsByName(WebAuthDialog)
    # setupUi

    def retranslateUi(self, WebAuthDialog):
        WebAuthDialog.setWindowTitle(QCoreApplication.translate("WebAuthDialog", u"Dialog", None))
        self.m_headingLabel.setText(QCoreApplication.translate("WebAuthDialog", u"Heading", None))
        self.m_description.setText(QCoreApplication.translate("WebAuthDialog", u"Description", None))
        self.m_pinGroupBox.setTitle("")
        self.m_pinLabel.setText(QCoreApplication.translate("WebAuthDialog", u"PIN", None))
        self.m_confirmPinLabel.setText(QCoreApplication.translate("WebAuthDialog", u"Confirm PIN", None))
        self.m_pinEntryErrorLabel.setText(QCoreApplication.translate("WebAuthDialog", u"TextLabel", None))
    # retranslateUi

