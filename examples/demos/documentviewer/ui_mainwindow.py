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
from PySide6.QtWidgets import (QApplication, QMainWindow, QMenu, QMenuBar,
    QScrollArea, QSizePolicy, QSplitter, QStatusBar,
    QTabWidget, QToolBar, QVBoxLayout, QWidget)
import rc_documentviewer

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(983, 602)
        icon = QIcon()
        icon.addFile(u":/demos/documentviewer/images/qt-logo.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        MainWindow.setWindowIcon(icon)
        self.actionOpen = QAction(MainWindow)
        self.actionOpen.setObjectName(u"actionOpen")
        icon1 = QIcon()
        icon1.addFile(u":/demos/documentviewer/images/open.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionOpen.setIcon(icon1)
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        icon2 = QIcon()
        iconThemeName = u"help-about"
        if QIcon.hasThemeIcon(iconThemeName):
            icon2 = QIcon.fromTheme(iconThemeName)
        else:
            icon2.addFile(u":/demos/documentviewer/images/help-about.svgz", QSize(), QIcon.Mode.Normal, QIcon.State.Off)

        self.actionAbout.setIcon(icon2)
        self.actionForward = QAction(MainWindow)
        self.actionForward.setObjectName(u"actionForward")
        icon3 = QIcon()
        icon3.addFile(u":/demos/documentviewer/images/go-next.svgz", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionForward.setIcon(icon3)
        self.actionBack = QAction(MainWindow)
        self.actionBack.setObjectName(u"actionBack")
        icon4 = QIcon()
        icon4.addFile(u":/demos/documentviewer/images/go-previous.svgz", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionBack.setIcon(icon4)
        self.actionPrint = QAction(MainWindow)
        self.actionPrint.setObjectName(u"actionPrint")
        self.actionPrint.setEnabled(False)
        icon5 = QIcon()
        iconThemeName = u"document-print"
        if QIcon.hasThemeIcon(iconThemeName):
            icon5 = QIcon.fromTheme(iconThemeName)
        else:
            icon5.addFile(u":/demos/documentviewer/images/print2x.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)

        self.actionPrint.setIcon(icon5)
        self.actionAboutQt = QAction(MainWindow)
        self.actionAboutQt.setObjectName(u"actionAboutQt")
        icon6 = QIcon()
        icon6.addFile(u":/demos/documentviewer/images/qt-logo.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        icon6.addFile(u":/demos/documentviewer/images/qt-logo.png", QSize(), QIcon.Mode.Normal, QIcon.State.On)
        self.actionAboutQt.setIcon(icon6)
        self.actionRecent = QAction(MainWindow)
        self.actionRecent.setObjectName(u"actionRecent")
        icon7 = QIcon()
        icon7.addFile(u":/demos/documentviewer/images/document-open-recent.svgz", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionRecent.setIcon(icon7)
        self.actionQuit = QAction(MainWindow)
        self.actionQuit.setObjectName(u"actionQuit")
        icon8 = QIcon(QIcon.fromTheme(u"application-exit"))
        self.actionQuit.setIcon(icon8)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setEnabled(True)
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.viewArea = QWidget(self.centralwidget)
        self.viewArea.setObjectName(u"viewArea")
        self.verticalLayout_2 = QVBoxLayout(self.viewArea)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.splitter = QSplitter(self.viewArea)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.tabWidget = QTabWidget(self.splitter)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setTabPosition(QTabWidget.TabPosition.West)
        self.bookmarkTab = QWidget()
        self.bookmarkTab.setObjectName(u"bookmarkTab")
        self.tabWidget.addTab(self.bookmarkTab, "")
        self.pagesTab = QWidget()
        self.pagesTab.setObjectName(u"pagesTab")
        self.tabWidget.addTab(self.pagesTab, "")
        self.splitter.addWidget(self.tabWidget)
        self.scrollArea = QScrollArea(self.splitter)
        self.scrollArea.setObjectName(u"scrollArea")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setMinimumSize(QSize(800, 0))
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 798, 472))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.splitter.addWidget(self.scrollArea)

        self.verticalLayout_2.addWidget(self.splitter)


        self.verticalLayout.addWidget(self.viewArea)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 983, 26))
        self.qtFileMenu = QMenu(self.menubar)
        self.qtFileMenu.setObjectName(u"qtFileMenu")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.mainToolBar = QToolBar(MainWindow)
        self.mainToolBar.setObjectName(u"mainToolBar")
        MainWindow.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.mainToolBar)

        self.menubar.addAction(self.qtFileMenu.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.qtFileMenu.addAction(self.actionOpen)
        self.qtFileMenu.addAction(self.actionRecent)
        self.qtFileMenu.addAction(self.actionPrint)
        self.qtFileMenu.addAction(self.actionQuit)
        self.menuHelp.addAction(self.actionAbout)
        self.menuHelp.addAction(self.actionAboutQt)
        self.mainToolBar.addAction(self.actionOpen)
        self.mainToolBar.addAction(self.actionRecent)
        self.mainToolBar.addAction(self.actionPrint)
        self.mainToolBar.addSeparator()
        self.mainToolBar.addAction(self.actionBack)
        self.mainToolBar.addAction(self.actionForward)
        self.mainToolBar.addSeparator()

        self.retranslateUi(MainWindow)
        self.actionQuit.triggered.connect(MainWindow.close)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Document Viewer Demo", None))
        self.actionOpen.setText(QCoreApplication.translate("MainWindow", u"Open", None))
#if QT_CONFIG(shortcut)
        self.actionOpen.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+O", None))
#endif // QT_CONFIG(shortcut)
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"about documentviewer", None))
#if QT_CONFIG(tooltip)
        self.actionAbout.setToolTip(QCoreApplication.translate("MainWindow", u"Show information about the Document Viewer deomo.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.actionAbout.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+H", None))
#endif // QT_CONFIG(shortcut)
        self.actionForward.setText(QCoreApplication.translate("MainWindow", u"actionForward", None))
#if QT_CONFIG(tooltip)
        self.actionForward.setToolTip(QCoreApplication.translate("MainWindow", u"One step forward", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.actionForward.setShortcut(QCoreApplication.translate("MainWindow", u"Right", None))
#endif // QT_CONFIG(shortcut)
        self.actionBack.setText(QCoreApplication.translate("MainWindow", u"actionBack", None))
#if QT_CONFIG(tooltip)
        self.actionBack.setToolTip(QCoreApplication.translate("MainWindow", u"One step back", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.actionBack.setShortcut(QCoreApplication.translate("MainWindow", u"Left", None))
#endif // QT_CONFIG(shortcut)
        self.actionPrint.setText(QCoreApplication.translate("MainWindow", u"Print", None))
#if QT_CONFIG(tooltip)
        self.actionPrint.setToolTip(QCoreApplication.translate("MainWindow", u"Print current file", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.actionPrint.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+P", None))
#endif // QT_CONFIG(shortcut)
        self.actionAboutQt.setText(QCoreApplication.translate("MainWindow", u"About Qt", None))
#if QT_CONFIG(tooltip)
        self.actionAboutQt.setToolTip(QCoreApplication.translate("MainWindow", u"Show Qt license information", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.actionAboutQt.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+I", None))
#endif // QT_CONFIG(shortcut)
        self.actionRecent.setText(QCoreApplication.translate("MainWindow", u"Recently opened...", None))
#if QT_CONFIG(shortcut)
        self.actionRecent.setShortcut(QCoreApplication.translate("MainWindow", u"Meta+R", None))
#endif // QT_CONFIG(shortcut)
        self.actionQuit.setText(QCoreApplication.translate("MainWindow", u"Quit", None))
#if QT_CONFIG(tooltip)
        self.actionQuit.setToolTip(QCoreApplication.translate("MainWindow", u"Quit the application", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.actionQuit.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Q", None))
#endif // QT_CONFIG(shortcut)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.bookmarkTab), QCoreApplication.translate("MainWindow", u"Pages", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.pagesTab), QCoreApplication.translate("MainWindow", u"Bookmarks", None))
        self.qtFileMenu.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
        self.mainToolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
    # retranslateUi

