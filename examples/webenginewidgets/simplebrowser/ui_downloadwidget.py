# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'downloadwidget.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QLabel,
    QLayout, QProgressBar, QPushButton, QSizePolicy,
    QWidget)

class Ui_DownloadWidget(object):
    def setupUi(self, DownloadWidget):
        if not DownloadWidget.objectName():
            DownloadWidget.setObjectName(u"DownloadWidget")
        DownloadWidget.resize(144, 103)
        DownloadWidget.setStyleSheet(u"#DownloadWidget {\n"
"  background: palette(button);\n"
"  border: 1px solid palette(dark);\n"
"  margin: 0px;\n"
"}")
        self.m_topLevelLayout = QGridLayout(DownloadWidget)
        self.m_topLevelLayout.setObjectName(u"m_topLevelLayout")
        self.m_topLevelLayout.setSizeConstraint(QLayout.SizeConstraint.SetMinAndMaxSize)
        self.m_dstName = QLabel(DownloadWidget)
        self.m_dstName.setObjectName(u"m_dstName")
        self.m_dstName.setStyleSheet(u"font-weight: bold\n"
"")

        self.m_topLevelLayout.addWidget(self.m_dstName, 0, 0, 1, 1)

        self.m_cancelButton = QPushButton(DownloadWidget)
        self.m_cancelButton.setObjectName(u"m_cancelButton")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.m_cancelButton.sizePolicy().hasHeightForWidth())
        self.m_cancelButton.setSizePolicy(sizePolicy)
        self.m_cancelButton.setStyleSheet(u"QPushButton {\n"
"  margin: 1px;\n"
"  border: none;\n"
"}\n"
"QPushButton:pressed {\n"
"  margin: none;\n"
"  border: 1px solid palette(shadow);\n"
"  background: palette(midlight);\n"
"}")
        self.m_cancelButton.setFlat(False)

        self.m_topLevelLayout.addWidget(self.m_cancelButton, 0, 1, 1, 1)

        self.m_srcUrl = QLabel(DownloadWidget)
        self.m_srcUrl.setObjectName(u"m_srcUrl")
        self.m_srcUrl.setMaximumSize(QSize(350, 16777215))
        self.m_srcUrl.setStyleSheet(u"")

        self.m_topLevelLayout.addWidget(self.m_srcUrl, 1, 0, 1, 2)

        self.m_progressBar = QProgressBar(DownloadWidget)
        self.m_progressBar.setObjectName(u"m_progressBar")
        self.m_progressBar.setStyleSheet(u"font-size: 12px")
        self.m_progressBar.setValue(24)

        self.m_topLevelLayout.addWidget(self.m_progressBar, 2, 0, 1, 2)


        self.retranslateUi(DownloadWidget)

        QMetaObject.connectSlotsByName(DownloadWidget)
    # setupUi

    def retranslateUi(self, DownloadWidget):
        self.m_dstName.setText(QCoreApplication.translate("DownloadWidget", u"TextLabel", None))
        self.m_srcUrl.setText(QCoreApplication.translate("DownloadWidget", u"TextLabel", None))
        pass
    # retranslateUi

