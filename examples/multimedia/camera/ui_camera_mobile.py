# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'camera_mobile.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QMainWindow, QMenu, QMenuBar,
    QPushButton, QSizePolicy, QSlider, QSpacerItem,
    QStackedWidget, QStatusBar, QTabWidget, QVBoxLayout,
    QWidget)

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
        self.centralwidget = QWidget(Camera)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_3 = QGridLayout(self.centralwidget)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.captureWidget = QTabWidget(self.centralwidget)
        self.captureWidget.setObjectName(u"captureWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.captureWidget.sizePolicy().hasHeightForWidth())
        self.captureWidget.setSizePolicy(sizePolicy)
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.gridLayout = QGridLayout(self.tab_2)
        self.gridLayout.setObjectName(u"gridLayout")
        self.exposureCompensation = QSlider(self.tab_2)
        self.exposureCompensation.setObjectName(u"exposureCompensation")
        self.exposureCompensation.setMinimum(-4)
        self.exposureCompensation.setMaximum(4)
        self.exposureCompensation.setPageStep(2)
        self.exposureCompensation.setOrientation(Qt.Orientation.Horizontal)
        self.exposureCompensation.setTickPosition(QSlider.TickPosition.TicksAbove)

        self.gridLayout.addWidget(self.exposureCompensation, 4, 0, 1, 1)

        self.label = QLabel(self.tab_2)
        self.label.setObjectName(u"label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.label, 3, 0, 1, 1)

        self.takeImageButton = QPushButton(self.tab_2)
        self.takeImageButton.setObjectName(u"takeImageButton")
        self.takeImageButton.setEnabled(False)
        icon = QIcon()
        icon.addFile(u":/images/shutter.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.takeImageButton.setIcon(icon)

        self.gridLayout.addWidget(self.takeImageButton, 0, 0, 1, 1)

        self.captureWidget.addTab(self.tab_2, "")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.gridLayout_2 = QGridLayout(self.tab)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.recordButton = QPushButton(self.tab)
        self.recordButton.setObjectName(u"recordButton")

        self.verticalLayout.addWidget(self.recordButton)

        self.pauseButton = QPushButton(self.tab)
        self.pauseButton.setObjectName(u"pauseButton")

        self.verticalLayout.addWidget(self.pauseButton)

        self.stopButton = QPushButton(self.tab)
        self.stopButton.setObjectName(u"stopButton")

        self.verticalLayout.addWidget(self.stopButton)


        self.horizontalLayout.addLayout(self.verticalLayout)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalSpacer = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.muteButton = QPushButton(self.tab)
        self.muteButton.setObjectName(u"muteButton")
        self.muteButton.setCheckable(True)

        self.verticalLayout_2.addWidget(self.muteButton)

        self.metaDataButton = QPushButton(self.tab)
        self.metaDataButton.setObjectName(u"metaDataButton")
        self.metaDataButton.setCheckable(True)

        self.verticalLayout_2.addWidget(self.metaDataButton)


        self.horizontalLayout.addLayout(self.verticalLayout_2)


        self.gridLayout_2.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        self.captureWidget.addTab(self.tab, "")

        self.gridLayout_3.addWidget(self.captureWidget, 1, 1, 1, 2)

        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(1)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.stackedWidget.sizePolicy().hasHeightForWidth())
        self.stackedWidget.setSizePolicy(sizePolicy2)
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
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.viewfinder.sizePolicy().hasHeightForWidth())
        self.viewfinder.setSizePolicy(sizePolicy3)

        self.gridLayout_5.addWidget(self.viewfinder, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.viewfinderPage)
        self.previewPage = QWidget()
        self.previewPage.setObjectName(u"previewPage")
        self.gridLayout_4 = QGridLayout(self.previewPage)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.lastImagePreviewLabel = QLabel(self.previewPage)
        self.lastImagePreviewLabel.setObjectName(u"lastImagePreviewLabel")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.lastImagePreviewLabel.sizePolicy().hasHeightForWidth())
        self.lastImagePreviewLabel.setSizePolicy(sizePolicy4)
        self.lastImagePreviewLabel.setFrameShape(QFrame.Shape.Box)

        self.gridLayout_4.addWidget(self.lastImagePreviewLabel, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.previewPage)

        self.gridLayout_3.addWidget(self.stackedWidget, 0, 2, 1, 1)

        Camera.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(Camera)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 668, 26))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuDevices = QMenu(self.menubar)
        self.menuDevices.setObjectName(u"menuDevices")
        Camera.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(Camera)
        self.statusbar.setObjectName(u"statusbar")
        Camera.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuDevices.menuAction())
        self.menuFile.addAction(self.actionStartCamera)
        self.menuFile.addAction(self.actionStopCamera)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSettings)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)

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
        self.actionExit.setText(QCoreApplication.translate("Camera", u"Close", None))
        self.actionStartCamera.setText(QCoreApplication.translate("Camera", u"Start Camera", None))
        self.actionStopCamera.setText(QCoreApplication.translate("Camera", u"Stop Camera", None))
        self.actionSettings.setText(QCoreApplication.translate("Camera", u"Change Settings", None))
        self.label.setText(QCoreApplication.translate("Camera", u"Exposure Compensation:", None))
        self.takeImageButton.setText(QCoreApplication.translate("Camera", u"Capture Photo", None))
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
    # retranslateUi

