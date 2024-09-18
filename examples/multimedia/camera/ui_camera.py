# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'camera.ui'
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
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QLabel,
    QMainWindow, QMenu, QMenuBar, QPushButton,
    QSizePolicy, QSlider, QSpacerItem, QStackedWidget,
    QStatusBar, QTabWidget, QWidget)

class Ui_Camera(object):
    def setupUi(self, Camera):
        if not Camera.objectName():
            Camera.setObjectName(u"Camera")
        Camera.resize(668, 429)
        self.actionExit = QAction(Camera)
        self.actionExit.setObjectName(u"actionExit")
        self.actionStartCamera = QAction(Camera)
        self.actionStartCamera.setObjectName(u"actionStartCamera")
        self.actionStopCamera = QAction(Camera)
        self.actionStopCamera.setObjectName(u"actionStopCamera")
        self.actionSettings = QAction(Camera)
        self.actionSettings.setObjectName(u"actionSettings")
        self.actionAbout_Qt = QAction(Camera)
        self.actionAbout_Qt.setObjectName(u"actionAbout_Qt")
        self.centralwidget = QWidget(Camera)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_3 = QGridLayout(self.centralwidget)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.captureWidget = QTabWidget(self.centralwidget)
        self.captureWidget.setObjectName(u"captureWidget")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.gridLayout = QGridLayout(self.tab_2)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalSpacer_2 = QSpacerItem(20, 161, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_2, 3, 0, 1, 1)

        self.takeImageButton = QPushButton(self.tab_2)
        self.takeImageButton.setObjectName(u"takeImageButton")
        self.takeImageButton.setEnabled(False)

        self.gridLayout.addWidget(self.takeImageButton, 0, 0, 1, 1)

        self.exposureCompensation = QSlider(self.tab_2)
        self.exposureCompensation.setObjectName(u"exposureCompensation")
        self.exposureCompensation.setMinimum(-4)
        self.exposureCompensation.setMaximum(4)
        self.exposureCompensation.setPageStep(2)
        self.exposureCompensation.setOrientation(Qt.Orientation.Horizontal)
        self.exposureCompensation.setTickPosition(QSlider.TickPosition.TicksAbove)

        self.gridLayout.addWidget(self.exposureCompensation, 5, 0, 1, 1)

        self.label = QLabel(self.tab_2)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 4, 0, 1, 1)

        self.captureWidget.addTab(self.tab_2, "")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.gridLayout_2 = QGridLayout(self.tab)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.recordButton = QPushButton(self.tab)
        self.recordButton.setObjectName(u"recordButton")

        self.gridLayout_2.addWidget(self.recordButton, 0, 0, 1, 1)

        self.pauseButton = QPushButton(self.tab)
        self.pauseButton.setObjectName(u"pauseButton")

        self.gridLayout_2.addWidget(self.pauseButton, 1, 0, 1, 1)

        self.stopButton = QPushButton(self.tab)
        self.stopButton.setObjectName(u"stopButton")

        self.gridLayout_2.addWidget(self.stopButton, 2, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 76, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer, 3, 0, 1, 1)

        self.muteButton = QPushButton(self.tab)
        self.muteButton.setObjectName(u"muteButton")
        self.muteButton.setCheckable(True)

        self.gridLayout_2.addWidget(self.muteButton, 4, 0, 1, 1)

        self.metaDataButton = QPushButton(self.tab)
        self.metaDataButton.setObjectName(u"metaDataButton")
        self.metaDataButton.setCheckable(True)

        self.gridLayout_2.addWidget(self.metaDataButton, 5, 0, 1, 1)

        self.captureWidget.addTab(self.tab, "")

        self.gridLayout_3.addWidget(self.captureWidget, 1, 1, 1, 2)

        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stackedWidget.sizePolicy().hasHeightForWidth())
        self.stackedWidget.setSizePolicy(sizePolicy)
        palette = QPalette()
        brush = QBrush(QColor(255, 255, 255, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Base, brush)
        brush1 = QBrush(QColor(145, 145, 145, 255))
        brush1.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Window, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Window, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Window, brush1)
        self.stackedWidget.setPalette(palette)
        self.viewfinderPage = QWidget()
        self.viewfinderPage.setObjectName(u"viewfinderPage")
        self.gridLayout_5 = QGridLayout(self.viewfinderPage)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.viewfinder = QVideoWidget(self.viewfinderPage)
        self.viewfinder.setObjectName(u"viewfinder")

        self.gridLayout_5.addWidget(self.viewfinder, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.viewfinderPage)
        self.previewPage = QWidget()
        self.previewPage.setObjectName(u"previewPage")
        self.gridLayout_4 = QGridLayout(self.previewPage)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.lastImagePreviewLabel = QLabel(self.previewPage)
        self.lastImagePreviewLabel.setObjectName(u"lastImagePreviewLabel")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.lastImagePreviewLabel.sizePolicy().hasHeightForWidth())
        self.lastImagePreviewLabel.setSizePolicy(sizePolicy1)
        self.lastImagePreviewLabel.setFrameShape(QFrame.Shape.Box)

        self.gridLayout_4.addWidget(self.lastImagePreviewLabel, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.previewPage)

        self.gridLayout_3.addWidget(self.stackedWidget, 0, 0, 2, 1)

        Camera.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(Camera)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 668, 26))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuDevices = QMenu(self.menubar)
        self.menuDevices.setObjectName(u"menuDevices")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        Camera.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(Camera)
        self.statusbar.setObjectName(u"statusbar")
        Camera.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuDevices.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionStartCamera)
        self.menuFile.addAction(self.actionStopCamera)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSettings)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuHelp.addAction(self.actionAbout_Qt)

        self.retranslateUi(Camera)
        self.recordButton.clicked.connect(Camera.record)
        self.stopButton.clicked.connect(Camera.stop)
        self.pauseButton.clicked.connect(Camera.pause)
        self.actionExit.triggered.connect(Camera.close)
        self.takeImageButton.clicked.connect(Camera.takeImage)
        self.muteButton.toggled.connect(Camera.setMuted)
        self.exposureCompensation.valueChanged.connect(Camera.setExposureCompensation)
        self.actionSettings.triggered.connect(Camera.configureCaptureSettings)
        self.actionStartCamera.triggered.connect(Camera.startCamera)
        self.actionStopCamera.triggered.connect(Camera.stopCamera)

        self.captureWidget.setCurrentIndex(0)
        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Camera)
    # setupUi

    def retranslateUi(self, Camera):
        Camera.setWindowTitle(QCoreApplication.translate("Camera", u"Camera", None))
        self.actionExit.setText(QCoreApplication.translate("Camera", u"Quit", None))
#if QT_CONFIG(shortcut)
        self.actionExit.setShortcut(QCoreApplication.translate("Camera", u"Ctrl+Q", None))
#endif // QT_CONFIG(shortcut)
        self.actionStartCamera.setText(QCoreApplication.translate("Camera", u"Start Camera", None))
        self.actionStopCamera.setText(QCoreApplication.translate("Camera", u"Stop Camera", None))
        self.actionSettings.setText(QCoreApplication.translate("Camera", u"Change Settings", None))
        self.actionAbout_Qt.setText(QCoreApplication.translate("Camera", u"About Qt", None))
        self.takeImageButton.setText(QCoreApplication.translate("Camera", u"Capture Photo", None))
        self.label.setText(QCoreApplication.translate("Camera", u"Exposure Compensation:", None))
        self.captureWidget.setTabText(self.captureWidget.indexOf(self.tab_2), QCoreApplication.translate("Camera", u"Image", None))
        self.recordButton.setText(QCoreApplication.translate("Camera", u"Record", None))
        self.pauseButton.setText(QCoreApplication.translate("Camera", u"Pause", None))
        self.stopButton.setText(QCoreApplication.translate("Camera", u"Stop", None))
        self.muteButton.setText(QCoreApplication.translate("Camera", u"Mute", None))
        self.metaDataButton.setText(QCoreApplication.translate("Camera", u"Set metadata", None))
        self.captureWidget.setTabText(self.captureWidget.indexOf(self.tab), QCoreApplication.translate("Camera", u"Video", None))
        self.lastImagePreviewLabel.setText("")
        self.menuFile.setTitle(QCoreApplication.translate("Camera", u"File", None))
        self.menuDevices.setTitle(QCoreApplication.translate("Camera", u"Devices", None))
        self.menuHelp.setTitle(QCoreApplication.translate("Camera", u"Help", None))
    # retranslateUi

