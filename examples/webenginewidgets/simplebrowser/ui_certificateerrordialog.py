# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'certificateerrordialog.ui'
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
    QLabel, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_CertificateErrorDialog(object):
    def setupUi(self, CertificateErrorDialog):
        if not CertificateErrorDialog.objectName():
            CertificateErrorDialog.setObjectName(u"CertificateErrorDialog")
        CertificateErrorDialog.resize(689, 204)
        self.verticalLayout = QVBoxLayout(CertificateErrorDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(20, -1, 20, -1)
        self.m_iconLabel = QLabel(CertificateErrorDialog)
        self.m_iconLabel.setObjectName(u"m_iconLabel")
        self.m_iconLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.m_iconLabel)

        self.m_errorLabel = QLabel(CertificateErrorDialog)
        self.m_errorLabel.setObjectName(u"m_errorLabel")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.m_errorLabel.sizePolicy().hasHeightForWidth())
        self.m_errorLabel.setSizePolicy(sizePolicy)
        self.m_errorLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.m_errorLabel.setWordWrap(True)

        self.verticalLayout.addWidget(self.m_errorLabel)

        self.m_infoLabel = QLabel(CertificateErrorDialog)
        self.m_infoLabel.setObjectName(u"m_infoLabel")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.m_infoLabel.sizePolicy().hasHeightForWidth())
        self.m_infoLabel.setSizePolicy(sizePolicy1)
        self.m_infoLabel.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.m_infoLabel.setWordWrap(True)

        self.verticalLayout.addWidget(self.m_infoLabel)

        self.verticalSpacer = QSpacerItem(20, 16, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.buttonBox = QDialogButtonBox(CertificateErrorDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.No|QDialogButtonBox.StandardButton.Yes)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(CertificateErrorDialog)
        self.buttonBox.accepted.connect(CertificateErrorDialog.accept)
        self.buttonBox.rejected.connect(CertificateErrorDialog.reject)

        QMetaObject.connectSlotsByName(CertificateErrorDialog)
    # setupUi

    def retranslateUi(self, CertificateErrorDialog):
        CertificateErrorDialog.setWindowTitle(QCoreApplication.translate("CertificateErrorDialog", u"Dialog", None))
        self.m_iconLabel.setText(QCoreApplication.translate("CertificateErrorDialog", u"Icon", None))
        self.m_errorLabel.setText(QCoreApplication.translate("CertificateErrorDialog", u"Error", None))
        self.m_infoLabel.setText(QCoreApplication.translate("CertificateErrorDialog", u"If you wish so, you may continue with an unverified certificate. Accepting an unverified certificate mean you may not be connected with the host you tried to connect to.\n"
"\n"
"Do you wish to override the security check and continue ?   ", None))
    # retranslateUi

