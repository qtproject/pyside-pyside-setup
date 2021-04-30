
#############################################################################
##
## Copyright (C) 2017 The Qt Company Ltd.
## Contact: http://www.qt.io/licensing/
##
## This file is part of the Qt for Python examples of the Qt Toolkit.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of The Qt Company Ltd nor the names of its
##     contributors may be used to endorse or promote products derived
##     from this software without specific prior written permission.
##
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
## $QT_END_LICENSE$
##
#############################################################################

"""PySide6 QtDataVisualization example"""

import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication, QSizePolicy, QMainWindow, QWidget
from PySide6.QtDataVisualization import (Q3DBars, QBar3DSeries, QBarDataItem,
                                         QCategory3DAxis, QValue3DAxis)


def data_to_bar_data_row(data):
    return list(QBarDataItem(d) for d in data)


def data_to_bar_data_array(data):
    return list(data_to_bar_data_row(row) for row in data)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle('Qt DataVisualization 3D Bars')

        self.bars = Q3DBars()

        self._column_axis = QCategory3DAxis()
        self._column_axis.setTitle('Columns')
        self._column_axis.setTitleVisible(True)
        self._column_axis.setLabels(['Column1', 'Column2'])
        self._column_axis.setLabelAutoRotation(30)

        self._row_axis = QCategory3DAxis()
        self._row_axis.setTitle('Rows')
        self._row_axis.setTitleVisible(True)
        self._row_axis.setLabels(['Row1', 'Row2'])
        self._row_axis.setLabelAutoRotation(30)

        self._value_axis = QValue3DAxis()
        self._value_axis.setTitle('Values')
        self._value_axis.setTitleVisible(True)
        self._value_axis.setRange(0, 5)

        self.bars.setRowAxis(self._row_axis)
        self.bars.setColumnAxis(self._column_axis)
        self.bars.setValueAxis(self._value_axis)

        self.series = QBar3DSeries()
        self._array_data = [[1, 2], [3, 4]]
        self.series.dataProxy().addRows(data_to_bar_data_array(self._array_data))

        self.bars.setPrimarySeries(self.series)

        self.container = QWidget.createWindowContainer(self.bars)

        if not self.bars.hasContext():
            print("Couldn't initialize the OpenGL context.")
            sys.exit(-1)

        camera = self.bars.scene().activeCamera()
        camera.setYRotation(22.5)

        geometry = QGuiApplication.primaryScreen().geometry()
        size = geometry.height() * 3 / 4
        self.container.setMinimumSize(size, size)

        self.container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.container.setFocusPolicy(Qt.StrongFocus)
        self.setCentralWidget(self.container)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())
