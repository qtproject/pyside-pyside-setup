# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from PySide6.QtCore import QObject, QMarginsF, QUrl, Qt, Property, Slot
from PySide6.QtGui import (QDesktopServices, QImage, QPageSize, QPainter, QPaintDevice,
                           QPdfWriter)
from PySide6.QtQml import QmlElement
from PySide6.QtPrintSupport import QPrinter, QPrinterInfo

QML_IMPORT_NAME = "GraphPrintingExample"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class GraphPrinter(QObject):

    def __init__(self, parent=None):
        super().__init__(parent)

    @Property(int, constant=True)
    def maxTextureSize(self):
        return 4096  # Use 4096 as the minimum

    def paintImage(self, image: QImage, device: QPaintDevice):
        painter = QPainter(device)
        viewportSize = painter.viewport().size()
        imageSize = image.size()
        print(f"Scaling {imageSize.width()}x{imageSize.height()} to "
              f"{viewportSize.width()}x{viewportSize.height()}.")
        finalImage = image.scaled(viewportSize, Qt.AspectRatioMode.KeepAspectRatio)
        painter.setRenderHint(QPainter.RenderHint.LosslessImageRendering)
        painter.drawImage(finalImage.rect(), finalImage)
        painter.end()

    def _generatePDF(self, fileName: str, image: QImage):
        writer = QPdfWriter(fileName)
        writer.setResolution(90)
        writer.setTitle("Graph")
        writer.setPageSize(QPageSize(image.size()))
        writer.setPageMargins(QMarginsF(0, 0, 0, 0))
        writer.newPage()
        self.paintImage(image, writer)

    @Slot(QUrl, QImage, result=str)
    def generatePDF(self, path: QUrl, image: QImage):
        fileName = path.toLocalFile()
        self._generatePDF(fileName, image)

        QDesktopServices.openUrl(path)

        return fileName

    @Slot(QImage, str, result=str)
    def print(self, image: QImage, printerName: str):
        printInfo = QPrinterInfo.printerInfo(printerName)
        if printInfo.isNull():
            return f"{printerName} is not a valid printer"

        printer = QPrinter(printInfo, QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.NativeFormat)
        self.paintImage(image, printer)

        return f"Printed to {printerName}"

    @Slot(result="QStringList")
    def getPrinters(self):
        return QPrinterInfo.availablePrinterNames()
