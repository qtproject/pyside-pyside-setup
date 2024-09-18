# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'passworddialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QGridLayout, QLabel, QLineEdit, QSizePolicy,
    QWidget)

class Ui_PasswordDialog(object):
    def setupUi(self, PasswordDialog):
        if not PasswordDialog.objectName():
            PasswordDialog.setObjectName(u"PasswordDialog")
        PasswordDialog.resize(399, 148)
        self.gridLayout = QGridLayout(PasswordDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.m_iconLabel = QLabel(PasswordDialog)
        self.m_iconLabel.setObjectName(u"m_iconLabel")
        self.m_iconLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.m_iconLabel, 0, 0, 1, 1)

        self.m_infoLabel = QLabel(PasswordDialog)
        self.m_infoLabel.setObjectName(u"m_infoLabel")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.m_infoLabel.sizePolicy().hasHeightForWidth())
        self.m_infoLabel.setSizePolicy(sizePolicy)
        self.m_infoLabel.setWordWrap(True)

        self.gridLayout.addWidget(self.m_infoLabel, 0, 1, 1, 1)

        self.userLabel = QLabel(PasswordDialog)
        self.userLabel.setObjectName(u"userLabel")

        self.gridLayout.addWidget(self.userLabel, 1, 0, 1, 1)

        self.m_userNameLineEdit = QLineEdit(PasswordDialog)
        self.m_userNameLineEdit.setObjectName(u"m_userNameLineEdit")

        self.gridLayout.addWidget(self.m_userNameLineEdit, 1, 1, 1, 1)

        self.passwordLabel = QLabel(PasswordDialog)
        self.passwordLabel.setObjectName(u"passwordLabel")

        self.gridLayout.addWidget(self.passwordLabel, 2, 0, 1, 1)

        self.m_passwordLineEdit = QLineEdit(PasswordDialog)
        self.m_passwordLineEdit.setObjectName(u"m_passwordLineEdit")
        self.m_passwordLineEdit.setEchoMode(QLineEdit.EchoMode.Password)

        self.gridLayout.addWidget(self.m_passwordLineEdit, 2, 1, 1, 1)

        self.buttonBox = QDialogButtonBox(PasswordDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 2)

        self.userLabel.raise_()
        self.m_userNameLineEdit.raise_()
        self.passwordLabel.raise_()
        self.m_passwordLineEdit.raise_()
        self.buttonBox.raise_()
        self.m_iconLabel.raise_()
        self.m_infoLabel.raise_()

        self.retranslateUi(PasswordDialog)
        self.buttonBox.accepted.connect(PasswordDialog.accept)
        self.buttonBox.rejected.connect(PasswordDialog.reject)

        QMetaObject.connectSlotsByName(PasswordDialog)
    # setupUi

    def retranslateUi(self, PasswordDialog):
        PasswordDialog.setWindowTitle(QCoreApplication.translate("PasswordDialog", u"Authentication Required", None))
        self.m_iconLabel.setText(QCoreApplication.translate("PasswordDialog", u"Icon", None))
        self.m_infoLabel.setText(QCoreApplication.translate("PasswordDialog", u"Info", None))
        self.userLabel.setText(QCoreApplication.translate("PasswordDialog", u"Username:", None))
        self.passwordLabel.setText(QCoreApplication.translate("PasswordDialog", u"Password:", None))
    # retranslateUi

