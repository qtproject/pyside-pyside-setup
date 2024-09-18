# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'downloadmanagerwidget.ui'
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
from PySide6.QtWidgets import (QApplication, QLabel, QLayout, QScrollArea,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_DownloadManagerWidget(object):
    def setupUi(self, DownloadManagerWidget):
        if not DownloadManagerWidget.objectName():
            DownloadManagerWidget.setObjectName(u"DownloadManagerWidget")
        DownloadManagerWidget.resize(400, 212)
        DownloadManagerWidget.setStyleSheet(u"#DownloadManagerWidget {\n"
"    background: palette(button)\n"
"}")
        self.m_topLevelLayout = QVBoxLayout(DownloadManagerWidget)
        self.m_topLevelLayout.setObjectName(u"m_topLevelLayout")
        self.m_topLevelLayout.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        self.m_topLevelLayout.setContentsMargins(0, 0, 0, 0)
        self.m_scrollArea = QScrollArea(DownloadManagerWidget)
        self.m_scrollArea.setObjectName(u"m_scrollArea")
        self.m_scrollArea.setStyleSheet(u"#m_scrollArea {\n"
"  margin: 2px;\n"
"  border: none;\n"
"}")
        self.m_scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.m_scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.m_scrollArea.setWidgetResizable(True)
        self.m_scrollArea.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.m_items = QWidget()
        self.m_items.setObjectName(u"m_items")
        self.m_items.setGeometry(QRect(0, 0, 382, 208))
        self.m_items.setStyleSheet(u"#m_items {background: palette(mid)}")
        self.m_itemsLayout = QVBoxLayout(self.m_items)
        self.m_itemsLayout.setSpacing(2)
        self.m_itemsLayout.setObjectName(u"m_itemsLayout")
        self.m_itemsLayout.setContentsMargins(3, 3, 3, 3)
        self.m_zeroItemsLabel = QLabel(self.m_items)
        self.m_zeroItemsLabel.setObjectName(u"m_zeroItemsLabel")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.m_zeroItemsLabel.sizePolicy().hasHeightForWidth())
        self.m_zeroItemsLabel.setSizePolicy(sizePolicy)
        self.m_zeroItemsLabel.setStyleSheet(u"color: palette(shadow)")
        self.m_zeroItemsLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.m_itemsLayout.addWidget(self.m_zeroItemsLabel)

        self.m_scrollArea.setWidget(self.m_items)

        self.m_topLevelLayout.addWidget(self.m_scrollArea)


        self.retranslateUi(DownloadManagerWidget)

        QMetaObject.connectSlotsByName(DownloadManagerWidget)
    # setupUi

    def retranslateUi(self, DownloadManagerWidget):
        DownloadManagerWidget.setWindowTitle(QCoreApplication.translate("DownloadManagerWidget", u"Downloads", None))
        self.m_zeroItemsLabel.setText(QCoreApplication.translate("DownloadManagerWidget", u"No downloads", None))
    # retranslateUi

