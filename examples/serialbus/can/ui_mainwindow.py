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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QGridLayout, QGroupBox,
    QHBoxLayout, QHeaderView, QLabel, QMainWindow,
    QMenu, QMenuBar, QSizePolicy, QSpacerItem,
    QStatusBar, QToolBar, QVBoxLayout, QWidget)

from receivedframesview import ReceivedFramesView
from sendframebox import SendFrameBox
import rc_can

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(634, 527)
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
        self.actionQuit = QAction(MainWindow)
        self.actionQuit.setObjectName(u"actionQuit")
        icon2 = QIcon()
        icon2.addFile(u":/images/application-exit.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionQuit.setIcon(icon2)
        self.actionAboutQt = QAction(MainWindow)
        self.actionAboutQt.setObjectName(u"actionAboutQt")
        self.actionClearLog = QAction(MainWindow)
        self.actionClearLog.setObjectName(u"actionClearLog")
        icon3 = QIcon()
        icon3.addFile(u":/images/clear.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionClearLog.setIcon(icon3)
        self.actionPluginDocumentation = QAction(MainWindow)
        self.actionPluginDocumentation.setObjectName(u"actionPluginDocumentation")
        self.actionResetController = QAction(MainWindow)
        self.actionResetController.setObjectName(u"actionResetController")
        self.actionDeviceInformation = QAction(MainWindow)
        self.actionDeviceInformation.setObjectName(u"actionDeviceInformation")
        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        self.verticalLayout = QVBoxLayout(self.centralWidget)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.sendFrameBox = SendFrameBox(self.centralWidget)
        self.sendFrameBox.setObjectName(u"sendFrameBox")

        self.verticalLayout.addWidget(self.sendFrameBox)

        self.receivedMessagesBox = QGroupBox(self.centralWidget)
        self.receivedMessagesBox.setObjectName(u"receivedMessagesBox")
        self.gridLayout = QGridLayout(self.receivedMessagesBox)
        self.gridLayout.setSpacing(6)
        self.gridLayout.setContentsMargins(11, 11, 11, 11)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.receivedFramesView = ReceivedFramesView(self.receivedMessagesBox)
        self.receivedFramesView.setObjectName(u"receivedFramesView")
        self.receivedFramesView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.receivedFramesView.setProperty(u"showDropIndicator", False)
        self.receivedFramesView.setDragDropOverwriteMode(False)
        self.receivedFramesView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.verticalLayout_2.addWidget(self.receivedFramesView)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.busStatus = QLabel(self.receivedMessagesBox)
        self.busStatus.setObjectName(u"busStatus")

        self.horizontalLayout.addWidget(self.busStatus)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout_2.addLayout(self.horizontalLayout)


        self.gridLayout.addLayout(self.verticalLayout_2, 0, 0, 1, 1)


        self.verticalLayout.addWidget(self.receivedMessagesBox)

        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 634, 26))
        self.menuCalls = QMenu(self.menuBar)
        self.menuCalls.setObjectName(u"menuCalls")
        self.menuHelp = QMenu(self.menuBar)
        self.menuHelp.setObjectName(u"menuHelp")
        MainWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QToolBar(MainWindow)
        self.mainToolBar.setObjectName(u"mainToolBar")
        MainWindow.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.mainToolBar)
        self.statusBar = QStatusBar(MainWindow)
        self.statusBar.setObjectName(u"statusBar")
        MainWindow.setStatusBar(self.statusBar)

        self.menuBar.addAction(self.menuCalls.menuAction())
        self.menuBar.addAction(self.menuHelp.menuAction())
        self.menuCalls.addAction(self.actionConnect)
        self.menuCalls.addAction(self.actionDisconnect)
        self.menuCalls.addAction(self.actionDeviceInformation)
        self.menuCalls.addSeparator()
        self.menuCalls.addAction(self.actionResetController)
        self.menuCalls.addSeparator()
        self.menuCalls.addAction(self.actionClearLog)
        self.menuCalls.addSeparator()
        self.menuCalls.addAction(self.actionQuit)
        self.menuHelp.addAction(self.actionPluginDocumentation)
        self.menuHelp.addAction(self.actionAboutQt)
        self.mainToolBar.addAction(self.actionConnect)
        self.mainToolBar.addAction(self.actionDisconnect)
        self.mainToolBar.addSeparator()
        self.mainToolBar.addAction(self.actionClearLog)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"CAN Example", None))
        self.actionConnect.setText(QCoreApplication.translate("MainWindow", u"&Connect", None))
        self.actionDisconnect.setText(QCoreApplication.translate("MainWindow", u"&Disconnect", None))
        self.actionQuit.setText(QCoreApplication.translate("MainWindow", u"&Quit", None))
        self.actionAboutQt.setText(QCoreApplication.translate("MainWindow", u"&About Qt", None))
        self.actionClearLog.setText(QCoreApplication.translate("MainWindow", u"Clear &Log", None))
        self.actionPluginDocumentation.setText(QCoreApplication.translate("MainWindow", u"Plugin Documentation", None))
#if QT_CONFIG(tooltip)
        self.actionPluginDocumentation.setToolTip(QCoreApplication.translate("MainWindow", u"Open plugin documentation in Webbrowser", None))
#endif // QT_CONFIG(tooltip)
        self.actionResetController.setText(QCoreApplication.translate("MainWindow", u"&Reset CAN Controller", None))
#if QT_CONFIG(tooltip)
        self.actionResetController.setToolTip(QCoreApplication.translate("MainWindow", u"Reset CAN Controller", None))
#endif // QT_CONFIG(tooltip)
        self.actionDeviceInformation.setText(QCoreApplication.translate("MainWindow", u"Device &Information...", None))
        self.sendFrameBox.setTitle(QCoreApplication.translate("MainWindow", u"Send CAN frame", None))
        self.receivedMessagesBox.setTitle(QCoreApplication.translate("MainWindow", u"Received CAN messages", None))
        self.busStatus.setText("")
        self.menuCalls.setTitle(QCoreApplication.translate("MainWindow", u"&Calls", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"&Help", None))
    # retranslateUi

