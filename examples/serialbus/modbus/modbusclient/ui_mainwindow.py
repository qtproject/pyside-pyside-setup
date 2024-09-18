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
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QGroupBox,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QMainWindow, QMenu,
    QMenuBar, QPushButton, QSizePolicy, QSpacerItem,
    QSpinBox, QStatusBar, QTreeView, QVBoxLayout,
    QWidget)
import rc_modbusclient

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(601, 378)
        MainWindow.setMaximumSize(QSize(16777215, 1000))
        self.actionConnect = QAction(MainWindow)
        self.actionConnect.setObjectName(u"actionConnect")
        icon = QIcon()
        icon.addFile(u":/images/connect.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionConnect.setIcon(icon)
        self.actionDisconnect = QAction(MainWindow)
        self.actionDisconnect.setObjectName(u"actionDisconnect")
        icon1 = QIcon()
        icon1.addFile(u":/images/disconnect.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionDisconnect.setIcon(icon1)
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        icon2 = QIcon()
        icon2.addFile(u":/images/application-exit.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionExit.setIcon(icon2)
        self.actionOptions = QAction(MainWindow)
        self.actionOptions.setObjectName(u"actionOptions")
        icon3 = QIcon()
        icon3.addFile(u":/images/settings.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionOptions.setIcon(icon3)
        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        self.verticalLayout = QVBoxLayout(self.centralWidget)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridLayout = QGridLayout()
        self.gridLayout.setSpacing(6)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_27 = QLabel(self.centralWidget)
        self.label_27.setObjectName(u"label_27")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_27.sizePolicy().hasHeightForWidth())
        self.label_27.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.label_27, 0, 5, 1, 1)

        self.connectButton = QPushButton(self.centralWidget)
        self.connectButton.setObjectName(u"connectButton")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.connectButton.sizePolicy().hasHeightForWidth())
        self.connectButton.setSizePolicy(sizePolicy1)
        self.connectButton.setCheckable(False)
        self.connectButton.setAutoDefault(False)

        self.gridLayout.addWidget(self.connectButton, 0, 7, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 0, 4, 1, 1)

        self.serverEdit = QSpinBox(self.centralWidget)
        self.serverEdit.setObjectName(u"serverEdit")
        sizePolicy1.setHeightForWidth(self.serverEdit.sizePolicy().hasHeightForWidth())
        self.serverEdit.setSizePolicy(sizePolicy1)
        self.serverEdit.setMinimum(1)
        self.serverEdit.setMaximum(247)

        self.gridLayout.addWidget(self.serverEdit, 0, 6, 1, 1)

        self.connectType = QComboBox(self.centralWidget)
        self.connectType.addItem("")
        self.connectType.addItem("")
        self.connectType.setObjectName(u"connectType")

        self.gridLayout.addWidget(self.connectType, 0, 1, 1, 1)

        self.label_2 = QLabel(self.centralWidget)
        self.label_2.setObjectName(u"label_2")
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.label_2, 0, 2, 1, 1)

        self.label = QLabel(self.centralWidget)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.portEdit = QLineEdit(self.centralWidget)
        self.portEdit.setObjectName(u"portEdit")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.portEdit.sizePolicy().hasHeightForWidth())
        self.portEdit.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.portEdit, 0, 3, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(6)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.groupBox_2 = QGroupBox(self.centralWidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setMinimumSize(QSize(250, 0))
        self.gridLayout_3 = QGridLayout(self.groupBox_2)
        self.gridLayout_3.setSpacing(6)
        self.gridLayout_3.setContentsMargins(11, 11, 11, 11)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.label_4 = QLabel(self.groupBox_2)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_3.addWidget(self.label_4, 0, 0, 1, 1)

        self.readAddress = QSpinBox(self.groupBox_2)
        self.readAddress.setObjectName(u"readAddress")
        self.readAddress.setMaximum(9)

        self.gridLayout_3.addWidget(self.readAddress, 0, 1, 1, 1)

        self.label_5 = QLabel(self.groupBox_2)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_3.addWidget(self.label_5, 1, 0, 1, 1)

        self.readSize = QComboBox(self.groupBox_2)
        self.readSize.addItem("")
        self.readSize.addItem("")
        self.readSize.addItem("")
        self.readSize.addItem("")
        self.readSize.addItem("")
        self.readSize.addItem("")
        self.readSize.addItem("")
        self.readSize.addItem("")
        self.readSize.addItem("")
        self.readSize.addItem("")
        self.readSize.setObjectName(u"readSize")

        self.gridLayout_3.addWidget(self.readSize, 1, 1, 1, 1)

        self.label_9 = QLabel(self.groupBox_2)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout_3.addWidget(self.label_9, 2, 0, 1, 1)

        self.readValue = QListWidget(self.groupBox_2)
        self.readValue.setObjectName(u"readValue")
        self.readValue.setMinimumSize(QSize(0, 0))

        self.gridLayout_3.addWidget(self.readValue, 3, 0, 1, 2)


        self.horizontalLayout_2.addWidget(self.groupBox_2)

        self.writeGroupBox = QGroupBox(self.centralWidget)
        self.writeGroupBox.setObjectName(u"writeGroupBox")
        self.writeGroupBox.setMinimumSize(QSize(225, 0))
        self.gridLayout_2 = QGridLayout(self.writeGroupBox)
        self.gridLayout_2.setSpacing(6)
        self.gridLayout_2.setContentsMargins(11, 11, 11, 11)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_7 = QLabel(self.writeGroupBox)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout_2.addWidget(self.label_7, 0, 0, 1, 1)

        self.writeValueTable = QTreeView(self.writeGroupBox)
        self.writeValueTable.setObjectName(u"writeValueTable")
        self.writeValueTable.setProperty(u"showDropIndicator", True)
        self.writeValueTable.setAlternatingRowColors(True)
        self.writeValueTable.setRootIsDecorated(False)
        self.writeValueTable.setUniformRowHeights(True)
        self.writeValueTable.setItemsExpandable(False)
        self.writeValueTable.setExpandsOnDoubleClick(False)
        self.writeValueTable.header().setVisible(True)

        self.gridLayout_2.addWidget(self.writeValueTable, 3, 0, 1, 2)

        self.writeAddress = QSpinBox(self.writeGroupBox)
        self.writeAddress.setObjectName(u"writeAddress")
        self.writeAddress.setMaximum(9)

        self.gridLayout_2.addWidget(self.writeAddress, 0, 1, 1, 1)

        self.label_8 = QLabel(self.writeGroupBox)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout_2.addWidget(self.label_8, 1, 0, 1, 1)

        self.writeSize = QComboBox(self.writeGroupBox)
        self.writeSize.addItem("")
        self.writeSize.addItem("")
        self.writeSize.addItem("")
        self.writeSize.addItem("")
        self.writeSize.addItem("")
        self.writeSize.addItem("")
        self.writeSize.addItem("")
        self.writeSize.addItem("")
        self.writeSize.addItem("")
        self.writeSize.addItem("")
        self.writeSize.setObjectName(u"writeSize")

        self.gridLayout_2.addWidget(self.writeSize, 1, 1, 1, 1)

        self.label_3 = QLabel(self.writeGroupBox)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_2.addWidget(self.label_3, 2, 0, 1, 1)


        self.horizontalLayout_2.addWidget(self.writeGroupBox)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_6 = QLabel(self.centralWidget)
        self.label_6.setObjectName(u"label_6")

        self.horizontalLayout.addWidget(self.label_6)

        self.writeTable = QComboBox(self.centralWidget)
        self.writeTable.setObjectName(u"writeTable")

        self.horizontalLayout.addWidget(self.writeTable)

        self.horizontalSpacer_2 = QSpacerItem(13, 17, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.readButton = QPushButton(self.centralWidget)
        self.readButton.setObjectName(u"readButton")
        sizePolicy1.setHeightForWidth(self.readButton.sizePolicy().hasHeightForWidth())
        self.readButton.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.readButton)

        self.writeButton = QPushButton(self.centralWidget)
        self.writeButton.setObjectName(u"writeButton")

        self.horizontalLayout.addWidget(self.writeButton)

        self.readWriteButton = QPushButton(self.centralWidget)
        self.readWriteButton.setObjectName(u"readWriteButton")
        self.readWriteButton.setEnabled(False)

        self.horizontalLayout.addWidget(self.readWriteButton)


        self.verticalLayout.addLayout(self.horizontalLayout)

        MainWindow.setCentralWidget(self.centralWidget)
        self.statusBar = QStatusBar(MainWindow)
        self.statusBar.setObjectName(u"statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 601, 26))
        self.menuDevice = QMenu(self.menuBar)
        self.menuDevice.setObjectName(u"menuDevice")
        self.menuToo_ls = QMenu(self.menuBar)
        self.menuToo_ls.setObjectName(u"menuToo_ls")
        MainWindow.setMenuBar(self.menuBar)
        QWidget.setTabOrder(self.connectType, self.portEdit)
        QWidget.setTabOrder(self.portEdit, self.serverEdit)
        QWidget.setTabOrder(self.serverEdit, self.connectButton)
        QWidget.setTabOrder(self.connectButton, self.readAddress)
        QWidget.setTabOrder(self.readAddress, self.readSize)
        QWidget.setTabOrder(self.readSize, self.readValue)
        QWidget.setTabOrder(self.readValue, self.writeAddress)
        QWidget.setTabOrder(self.writeAddress, self.writeSize)
        QWidget.setTabOrder(self.writeSize, self.writeValueTable)
        QWidget.setTabOrder(self.writeValueTable, self.writeTable)
        QWidget.setTabOrder(self.writeTable, self.readButton)
        QWidget.setTabOrder(self.readButton, self.writeButton)
        QWidget.setTabOrder(self.writeButton, self.readWriteButton)

        self.menuBar.addAction(self.menuDevice.menuAction())
        self.menuBar.addAction(self.menuToo_ls.menuAction())
        self.menuDevice.addAction(self.actionConnect)
        self.menuDevice.addAction(self.actionDisconnect)
        self.menuDevice.addSeparator()
        self.menuDevice.addAction(self.actionExit)
        self.menuToo_ls.addAction(self.actionOptions)

        self.retranslateUi(MainWindow)

        self.connectButton.setDefault(True)
        self.readSize.setCurrentIndex(9)
        self.writeSize.setCurrentIndex(9)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Modbus Client Example", None))
        self.actionConnect.setText(QCoreApplication.translate("MainWindow", u"&Connect", None))
        self.actionDisconnect.setText(QCoreApplication.translate("MainWindow", u"&Disconnect", None))
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"&Quit", None))
        self.actionOptions.setText(QCoreApplication.translate("MainWindow", u"&Options", None))
        self.label_27.setText(QCoreApplication.translate("MainWindow", u"Server Address:", None))
        self.connectButton.setText(QCoreApplication.translate("MainWindow", u"Connect", None))
        self.connectType.setItemText(0, QCoreApplication.translate("MainWindow", u"Serial", None))
        self.connectType.setItemText(1, QCoreApplication.translate("MainWindow", u"TCP", None))

        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Port:", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Connection type:", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"Read", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Start address:", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Number of values:", None))
        self.readSize.setItemText(0, QCoreApplication.translate("MainWindow", u"1", None))
        self.readSize.setItemText(1, QCoreApplication.translate("MainWindow", u"2", None))
        self.readSize.setItemText(2, QCoreApplication.translate("MainWindow", u"3", None))
        self.readSize.setItemText(3, QCoreApplication.translate("MainWindow", u"4", None))
        self.readSize.setItemText(4, QCoreApplication.translate("MainWindow", u"5", None))
        self.readSize.setItemText(5, QCoreApplication.translate("MainWindow", u"6", None))
        self.readSize.setItemText(6, QCoreApplication.translate("MainWindow", u"7", None))
        self.readSize.setItemText(7, QCoreApplication.translate("MainWindow", u"8", None))
        self.readSize.setItemText(8, QCoreApplication.translate("MainWindow", u"9", None))
        self.readSize.setItemText(9, QCoreApplication.translate("MainWindow", u"10", None))

        self.label_9.setText(QCoreApplication.translate("MainWindow", u"Result:", None))
        self.writeGroupBox.setTitle(QCoreApplication.translate("MainWindow", u"Write", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Start address:", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Number of values:", None))
        self.writeSize.setItemText(0, QCoreApplication.translate("MainWindow", u"1", None))
        self.writeSize.setItemText(1, QCoreApplication.translate("MainWindow", u"2", None))
        self.writeSize.setItemText(2, QCoreApplication.translate("MainWindow", u"3", None))
        self.writeSize.setItemText(3, QCoreApplication.translate("MainWindow", u"4", None))
        self.writeSize.setItemText(4, QCoreApplication.translate("MainWindow", u"5", None))
        self.writeSize.setItemText(5, QCoreApplication.translate("MainWindow", u"6", None))
        self.writeSize.setItemText(6, QCoreApplication.translate("MainWindow", u"7", None))
        self.writeSize.setItemText(7, QCoreApplication.translate("MainWindow", u"8", None))
        self.writeSize.setItemText(8, QCoreApplication.translate("MainWindow", u"9", None))
        self.writeSize.setItemText(9, QCoreApplication.translate("MainWindow", u"10", None))

        self.label_3.setText("")
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Table:", None))
        self.readButton.setText(QCoreApplication.translate("MainWindow", u"Read", None))
        self.writeButton.setText(QCoreApplication.translate("MainWindow", u"Write", None))
        self.readWriteButton.setText(QCoreApplication.translate("MainWindow", u"Read-Write", None))
        self.menuDevice.setTitle(QCoreApplication.translate("MainWindow", u"&Device", None))
        self.menuToo_ls.setTitle(QCoreApplication.translate("MainWindow", u"Too&ls", None))
    # retranslateUi

