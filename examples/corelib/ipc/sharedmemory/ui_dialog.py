# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dialog.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QGridLayout, QLabel,
    QPushButton, QSizePolicy, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(451, 322)
        self.gridLayout = QGridLayout(Dialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.loadFromFileButton = QPushButton(Dialog)
        self.loadFromFileButton.setObjectName(u"loadFromFileButton")

        self.gridLayout.addWidget(self.loadFromFileButton, 0, 0, 1, 1)

        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)

        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)

        self.loadFromSharedMemoryButton = QPushButton(Dialog)
        self.loadFromSharedMemoryButton.setObjectName(u"loadFromSharedMemoryButton")

        self.gridLayout.addWidget(self.loadFromSharedMemoryButton, 2, 0, 1, 1)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.loadFromFileButton.setText(QCoreApplication.translate("Dialog", u"Load Image From File...", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Launch two of these dialogs.  In the first, press the top button and load an image from a file.  In the second, press the bottom button and display the loaded image from shared memory.", None))
        self.loadFromSharedMemoryButton.setText(QCoreApplication.translate("Dialog", u"Display Image From Shared Memory", None))
    # retranslateUi

