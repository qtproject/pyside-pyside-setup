#############################################################################
##
## Copyright (C) 2022 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
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

import os
import sys

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QGuiApplication, QVector3D
from PySide6.QtDataVisualization import (Q3DSurface, QSurfaceDataItem,
                                         QSurface3DSeries)


DESCRIPTION = """Minimal Qt DataVisualization Surface Example

Use the mouse wheel to zoom. Rotate using the right mouse button.
"""


if __name__ == '__main__':
    os.environ["QSG_RHI_BACKEND"] = "opengl"
    app = QGuiApplication(sys.argv)

    print(DESCRIPTION)

    surface = Q3DSurface()
    surface.setFlags(surface.flags() ^ Qt.FramelessWindowHint)
    axis = surface.axisX()
    axis.setTitle("X")
    axis.setTitleVisible(True)
    axis = surface.axisY()
    axis.setTitle("Y")
    axis.setTitleVisible(True)
    axis = surface.axisZ()
    axis.setTitle("Z")
    axis.setTitleVisible(True)

    data = []
    data_row1 = [QSurfaceDataItem(QVector3D(0, 0.1, 0.5)),
                 QSurfaceDataItem(QVector3D(1, 0.5, 0.5))]
    data.append(data_row1)
    data_row2 = [QSurfaceDataItem(QVector3D(0, 1.8, 1)),
                 QSurfaceDataItem(QVector3D(1, 1.2, 1))]
    data.append(data_row2)

    series = QSurface3DSeries()
    series.dataProxy().resetArray(data)
    surface.addSeries(series)

    available_height = app.primaryScreen().availableGeometry().height()
    width = available_height * 4 / 5
    surface.resize(QSize(width, width))
    surface.show()

    sys.exit(app.exec())
