
#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited.
## Copyright (C) 2016 The Qt Company Ltd.
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

"""PySide6 port of the corelib/threads/mandelbrot example from Qt v5.x, originating from PyQt"""

from argparse import ArgumentParser, RawTextHelpFormatter
import sys

from PySide6.QtCore import (Signal, QMutex, QElapsedTimer, QMutexLocker,
                            QPoint, QPointF, QSize, Qt, QThread,
                            QWaitCondition)
from PySide6.QtGui import QColor, QImage, QPainter, QPixmap, qRgb
from PySide6.QtWidgets import QApplication, QWidget


DEFAULT_CENTER_X = -0.647011
DEFAULT_CENTER_Y = -0.0395159
DEFAULT_SCALE = 0.00403897

ZOOM_IN_FACTOR = 0.8
ZOOM_OUT_FACTOR = 1 / ZOOM_IN_FACTOR
SCROLL_STEP = 20


NUM_PASSES = 8


INFO_KEY = 'info'


HELP = ("Use mouse wheel or the '+' and '-' keys to zoom. Press and "
       "hold left mouse button to scroll.")


class RenderThread(QThread):
    colormap_size = 512

    rendered_image = Signal(QImage, float)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.mutex = QMutex()
        self.condition = QWaitCondition()
        self._center_x = 0.0
        self._center_y = 0.0
        self._scale_factor = 0.0
        self._result_size = QSize()
        self.colormap = []

        self.restart = False
        self.abort = False

        for i in range(RenderThread.colormap_size):
            self.colormap.append(self.rgb_from_wave_length(380.0 + (i * 400.0 / RenderThread.colormap_size)))

    def stop(self):
        self.mutex.lock()
        self.abort = True
        self.condition.wakeOne()
        self.mutex.unlock()

        self.wait(2000)

    def render(self, centerX, centerY, scale_factor, resultSize):
        locker = QMutexLocker(self.mutex)

        self._center_x = centerX
        self._center_y = centerY
        self._scale_factor = scale_factor
        self._result_size = resultSize

        if not self.isRunning():
            self.start(QThread.LowPriority)
        else:
            self.restart = True
            self.condition.wakeOne()

    def run(self):
        timer = QElapsedTimer()

        while True:
            self.mutex.lock()
            resultSize = self._result_size
            scale_factor = self._scale_factor
            centerX = self._center_x
            centerY = self._center_y
            self.mutex.unlock()

            half_width = resultSize.width() // 2
            half_height = resultSize.height() // 2
            image = QImage(resultSize, QImage.Format_RGB32)

            curpass = 0

            while curpass < NUM_PASSES:
                timer.restart()
                max_iterations = (1 << (2 * curpass + 6)) + 32
                LIMIT = 4
                all_black = True

                for y in range(-half_height, half_height):
                    if self.restart:
                        break
                    if self.abort:
                        return

                    ay = 1j * (centerY + (y * scale_factor))

                    for x in range(-half_width, half_width):
                        c0 = centerX + (x * scale_factor) + ay
                        c = c0
                        num_iterations = 0

                        while num_iterations < max_iterations:
                            num_iterations += 1
                            c = c * c + c0
                            if abs(c) >= LIMIT:
                                break
                            num_iterations += 1
                            c = c * c + c0
                            if abs(c) >= LIMIT:
                                break
                            num_iterations += 1
                            c = c * c + c0
                            if abs(c) >= LIMIT:
                                break
                            num_iterations += 1
                            c = c * c + c0
                            if abs(c) >= LIMIT:
                                break

                        if num_iterations < max_iterations:
                            image.setPixel(x + half_width, y + half_height,
                                           self.colormap[num_iterations % RenderThread.colormap_size])
                            all_black = False
                        else:
                            image.setPixel(x + half_width, y + half_height, qRgb(0, 0, 0))

                if all_black and curpass == 0:
                    curpass = 4
                else:
                    if not self.restart:
                        elapsed = timer.elapsed()
                        unit = 'ms'
                        if elapsed > 2000:
                            elapsed /= 1000
                            unit = 's'
                        text = f"Pass {curpass+1}/{NUM_PASSES}, max iterations: {max_iterations}, time: {elapsed}{unit}"
                        image.setText(INFO_KEY, text)
                        self.rendered_image.emit(image, scale_factor)
                    curpass += 1

            self.mutex.lock()
            if not self.restart:
                self.condition.wait(self.mutex)
            self.restart = False
            self.mutex.unlock()

    def rgb_from_wave_length(self, wave):
        r = 0.0
        g = 0.0
        b = 0.0

        if wave >= 380.0 and wave <= 440.0:
            r = -1.0 * (wave - 440.0) / (440.0 - 380.0)
            b = 1.0
        elif wave >= 440.0 and wave <= 490.0:
            g = (wave - 440.0) / (490.0 - 440.0)
            b = 1.0
        elif wave >= 490.0 and wave <= 510.0:
            g = 1.0
            b = -1.0 * (wave - 510.0) / (510.0 - 490.0)
        elif wave >= 510.0 and wave <= 580.0:
            r = (wave - 510.0) / (580.0 - 510.0)
            g = 1.0
        elif wave >= 580.0 and wave <= 645.0:
            r = 1.0
            g = -1.0 * (wave - 645.0) / (645.0 - 580.0)
        elif wave >= 645.0 and wave <= 780.0:
            r = 1.0

        s = 1.0
        if wave > 700.0:
            s = 0.3 + 0.7 * (780.0 - wave) / (780.0 - 700.0)
        elif wave < 420.0:
            s = 0.3 + 0.7 * (wave - 380.0) / (420.0 - 380.0)

        r = pow(r * s, 0.8)
        g = pow(g * s, 0.8)
        b = pow(b * s, 0.8)

        return qRgb(r * 255, g * 255, b * 255)


class MandelbrotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.thread = RenderThread()
        self.pixmap = QPixmap()
        self._pixmap_offset = QPointF()
        self._last_drag_pos = QPointF()

        self._center_x = DEFAULT_CENTER_X
        self._center_y = DEFAULT_CENTER_Y
        self._pixmap_scale = DEFAULT_SCALE
        self._cur_scale = DEFAULT_SCALE

        self.thread.rendered_image.connect(self.update_pixmap)

        self.setWindowTitle("Mandelbrot")
        self.setCursor(Qt.CrossCursor)
        self._info = ''

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.black)

        if self.pixmap.isNull():
            painter.setPen(Qt.white)
            painter.drawText(self.rect(), Qt.AlignCenter,
                    "Rendering initial image, please wait...")
            return

        if self._cur_scale == self._pixmap_scale:
            painter.drawPixmap(self._pixmap_offset, self.pixmap)
        else:
            scale_factor = self._pixmap_scale / self._cur_scale
            new_width = int(self.pixmap.width() * scale_factor)
            new_height = int(self.pixmap.height() * scale_factor)
            new_x = self._pixmap_offset.x() + (self.pixmap.width() - new_width) / 2
            new_y = self._pixmap_offset.y() + (self.pixmap.height() - new_height) / 2

            painter.save()
            painter.translate(new_x, new_y)
            painter.scale(scale_factor, scale_factor)
            exposed, _ = painter.transform().inverted()
            exposed = exposed.mapRect(self.rect()).adjusted(-1, -1, 1, 1)
            painter.drawPixmap(exposed, self.pixmap, exposed)
            painter.restore()

        text = HELP
        if self._info:
            text += ' ' + self._info
        metrics = painter.fontMetrics()
        text_width = metrics.horizontalAdvance(text)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 127))
        painter.drawRect((self.width() - text_width) / 2 - 5, 0, text_width + 10,
                metrics.lineSpacing() + 5)
        painter.setPen(Qt.white)
        painter.drawText((self.width() - text_width) / 2,
                metrics.leading() + metrics.ascent(), text)

    def resizeEvent(self, event):
        self.thread.render(self._center_x, self._center_y, self._cur_scale, self.size())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Plus:
            self.zoom(ZOOM_IN_FACTOR)
        elif event.key() == Qt.Key_Minus:
            self.zoom(ZOOM_OUT_FACTOR)
        elif event.key() == Qt.Key_Left:
            self.scroll(-SCROLL_STEP, 0)
        elif event.key() == Qt.Key_Right:
            self.scroll(+SCROLL_STEP, 0)
        elif event.key() == Qt.Key_Down:
            self.scroll(0, -SCROLL_STEP)
        elif event.key() == Qt.Key_Up:
            self.scroll(0, +SCROLL_STEP)
        elif event.key() == Qt.Key_Q:
            self.close()
        else:
            super(MandelbrotWidget, self).keyPressEvent(event)

    def wheelEvent(self, event):
        num_degrees = event.angleDelta().y() / 8
        num_steps = num_degrees / 15.0
        self.zoom(pow(ZOOM_IN_FACTOR, num_steps))

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self._last_drag_pos = event.position()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            pos = event.position()
            self._pixmap_offset += pos - self._last_drag_pos
            self._last_drag_pos = pos
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.position()
            self._pixmap_offset += pos - self._last_drag_pos
            self._last_drag_pos = QPointF()

            delta_x = (self.width() - self.pixmap.width()) / 2 - self._pixmap_offset.x()
            delta_y = (self.height() - self.pixmap.height()) / 2 - self._pixmap_offset.y()
            self.scroll(delta_x, delta_y)

    def update_pixmap(self, image, scale_factor):
        if not self._last_drag_pos.isNull():
            return

        self._info = image.text(INFO_KEY)
        self.pixmap = QPixmap.fromImage(image)
        self._pixmap_offset = QPointF()
        self._last_drag_position = QPointF()
        self._pixmap_scale = scale_factor
        self.update()

    def zoom(self, zoomFactor):
        self._cur_scale *= zoomFactor
        self.update()
        self.thread.render(self._center_x, self._center_y, self._cur_scale,
                self.size())

    def scroll(self, deltaX, deltaY):
        self._center_x += deltaX * self._cur_scale
        self._center_y += deltaY * self._cur_scale
        self.update()
        self.thread.render(self._center_x, self._center_y, self._cur_scale,
                self.size())


if __name__ == '__main__':
    parser = ArgumentParser(description='Qt Mandelbrot Example',
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument('--passes', '-p', type=int, help='Number of passes (1-8)')
    options = parser.parse_args()
    if options.passes:
        NUM_PASSES = int(options.passes)
        if NUM_PASSES < 1 or NUM_PASSES > 8:
            print(f'Invalid value: {options.passes}')
            sys.exit(-1)

    app = QApplication(sys.argv)
    widget = MandelbrotWidget()
    geometry = widget.screen().availableGeometry()
    widget.resize((2 * geometry.size()) / 3)
    pos = (geometry.size() - widget.size()) / 2
    widget.move(geometry.topLeft() + QPoint(pos.width(), pos.height()))

    widget.show()
    r = app.exec()
    widget.thread.stop()
    sys.exit(r)
