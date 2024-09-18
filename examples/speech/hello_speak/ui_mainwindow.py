# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QHBoxLayout,
    QLabel, QMainWindow, QPlainTextEdit, QPushButton,
    QSizePolicy, QSlider, QSpacerItem, QStatusBar,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(551, 448)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.plainTextEdit = QPlainTextEdit(self.centralwidget)
        self.plainTextEdit.setObjectName(u"plainTextEdit")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plainTextEdit.sizePolicy().hasHeightForWidth())
        self.plainTextEdit.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.plainTextEdit)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_5 = QLabel(self.centralwidget)
        self.label_5.setObjectName(u"label_5")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy1)
        self.label_5.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)

        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")
        sizePolicy1.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy1)
        self.label_3.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)

        self.label_4 = QLabel(self.centralwidget)
        self.label_4.setObjectName(u"label_4")
        sizePolicy1.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy1)
        self.label_4.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_4, 5, 0, 1, 1)

        self.pitch = QSlider(self.centralwidget)
        self.pitch.setObjectName(u"pitch")
        self.pitch.setMinimum(-10)
        self.pitch.setMaximum(10)
        self.pitch.setSingleStep(1)
        self.pitch.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout.addWidget(self.pitch, 3, 2, 1, 1)

        self.label_6 = QLabel(self.centralwidget)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_6, 6, 0, 1, 1)

        self.volume = QSlider(self.centralwidget)
        self.volume.setObjectName(u"volume")
        self.volume.setMaximum(100)
        self.volume.setSingleStep(5)
        self.volume.setPageStep(20)
        self.volume.setValue(70)
        self.volume.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout.addWidget(self.volume, 1, 2, 1, 1)

        self.language = QComboBox(self.centralwidget)
        self.language.setObjectName(u"language")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.language.sizePolicy().hasHeightForWidth())
        self.language.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.language, 5, 2, 1, 1)

        self.voice = QComboBox(self.centralwidget)
        self.voice.setObjectName(u"voice")

        self.gridLayout.addWidget(self.voice, 6, 2, 1, 1)

        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        sizePolicy1.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy1)
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)

        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        sizePolicy1.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy1)
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.rate = QSlider(self.centralwidget)
        self.rate.setObjectName(u"rate")
        self.rate.setMinimum(-10)
        self.rate.setMaximum(10)
        self.rate.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout.addWidget(self.rate, 2, 2, 1, 1)

        self.engine = QComboBox(self.centralwidget)
        self.engine.setObjectName(u"engine")
        sizePolicy2.setHeightForWidth(self.engine.sizePolicy().hasHeightForWidth())
        self.engine.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.engine, 4, 2, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.speakButton = QPushButton(self.centralwidget)
        self.speakButton.setObjectName(u"speakButton")

        self.horizontalLayout.addWidget(self.speakButton)

        self.pauseButton = QPushButton(self.centralwidget)
        self.pauseButton.setObjectName(u"pauseButton")
        self.pauseButton.setEnabled(False)

        self.horizontalLayout.addWidget(self.pauseButton)

        self.resumeButton = QPushButton(self.centralwidget)
        self.resumeButton.setObjectName(u"resumeButton")
        self.resumeButton.setEnabled(False)

        self.horizontalLayout.addWidget(self.resumeButton)

        self.stopButton = QPushButton(self.centralwidget)
        self.stopButton.setObjectName(u"stopButton")

        self.horizontalLayout.addWidget(self.stopButton)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
#if QT_CONFIG(shortcut)
        self.label_4.setBuddy(self.language)
#endif // QT_CONFIG(shortcut)
        QWidget.setTabOrder(self.plainTextEdit, self.speakButton)
        QWidget.setTabOrder(self.speakButton, self.pauseButton)
        QWidget.setTabOrder(self.pauseButton, self.resumeButton)
        QWidget.setTabOrder(self.resumeButton, self.stopButton)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.plainTextEdit.setPlainText(QCoreApplication.translate("MainWindow", u"Hello QtTextToSpeech,\n"
"this is an example text in English.\n"
"\n"
"QtSpeech is a library that makes text to speech easy with Qt.\n"
"Done, over and out.", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Engine", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Pitch:", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"&Language:", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Voice name:", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Rate:", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Volume:", None))
        self.speakButton.setText(QCoreApplication.translate("MainWindow", u"Speak", None))
        self.pauseButton.setText(QCoreApplication.translate("MainWindow", u"Pause", None))
        self.resumeButton.setText(QCoreApplication.translate("MainWindow", u"Resume", None))
        self.stopButton.setText(QCoreApplication.translate("MainWindow", u"Stop", None))
    # retranslateUi

