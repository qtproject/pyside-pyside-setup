# Copyright (C) 2010 Riverbank Computing Limited.
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from enum import IntEnum
import sys

from PySide6.QtCore import (Property, QEasingCurve, QObject, QPropertyAnimation,
                            QPoint, QPointF, QRect, QRectF, QSize, Qt)
from PySide6.QtGui import (QBrush, QColor, QIcon, QLinearGradient, QPainter,
                           QPainterPath, QPixmap)
from PySide6.QtWidgets import (QApplication, QGraphicsPixmapItem,
                               QGraphicsItem, QGraphicsScene,
                               QListWidgetItem, QWidget)

from ui_form import Ui_Form


class PathType(IntEnum):
    LINEAR_PATH = 0
    CIRCLE_PATH = 1


class Animation(QPropertyAnimation):
    def __init__(self, target, prop):
        super().__init__(target, prop)
        self.set_path_type(PathType.LINEAR_PATH)

    def set_path_type(self, pathType):
        self._pathType = pathType
        self._path = QPainterPath()

    def updateCurrentTime(self, currentTime):
        if self._pathType == PathType.CIRCLE_PATH:
            if self._path.isEmpty():
                end = self.endValue()
                start = self.startValue()
                self._path.moveTo(start)
                self._path.addEllipse(QRectF(start, end))

            dura = self.duration()
            if dura == 0:
                progress = 1.0
            else:
                progress = (((currentTime - 1) % dura) + 1) / float(dura)

            eased_progress = self.easingCurve().valueForProgress(progress)
            if eased_progress > 1.0:
                eased_progress -= 1.0
            elif eased_progress < 0:
                eased_progress += 1.0

            pt = self._path.pointAtPercent(eased_progress)
            self.updateCurrentValue(pt)
            self.valueChanged.emit(pt)
        else:
            super(Animation, self).updateCurrentTime(currentTime)


# PySide6 doesn't support deriving from more than one wrapped class so we use
# composition and delegate the property.
class Pixmap(QObject):
    def __init__(self, pix):
        super().__init__()

        self.pixmap_item = QGraphicsPixmapItem(pix)
        self.pixmap_item.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

    def set_pos(self, pos):
        self.pixmap_item.setPos(pos)

    def get_pos(self):
        return self.pixmap_item.pos()

    pos = Property(QPointF, get_pos, set_pos)


class Window(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._iconSize = QSize(64, 64)
        self._scene = QGraphicsScene()

        m_ui = Ui_Form()
        m_ui.setupUi(self)
        m_ui.easingCurvePicker.setIconSize(self._iconSize)
        m_ui.easingCurvePicker.setMinimumHeight(self._iconSize.height() + 50)
        m_ui.buttonGroup.setId(m_ui.lineRadio, 0)
        m_ui.buttonGroup.setId(m_ui.circleRadio, 1)

        dummy = QEasingCurve()
        m_ui.periodSpinBox.setValue(dummy.period())
        m_ui.amplitudeSpinBox.setValue(dummy.amplitude())
        m_ui.overshootSpinBox.setValue(dummy.overshoot())

        m_ui.easingCurvePicker.currentRowChanged.connect(self.curve_changed)
        m_ui.buttonGroup.idClicked.connect(self.path_changed)
        m_ui.periodSpinBox.valueChanged.connect(self.period_changed)
        m_ui.amplitudeSpinBox.valueChanged.connect(self.amplitude_changed)
        m_ui.overshootSpinBox.valueChanged.connect(self.overshoot_changed)

        self._ui = m_ui
        self.create_curve_icons()

        pix = QPixmap(':/qt-project.org/logos/pysidelogo.png')
        self._item = Pixmap(pix)
        self._scene.addItem(self._item.pixmap_item)
        self._ui.graphicsView.setScene(self._scene)

        self._anim = Animation(self._item, b'pos')
        self._anim.setEasingCurve(QEasingCurve.OutBounce)
        self._ui.easingCurvePicker.setCurrentRow(0)

        self.start_animation()

    def create_curve_icons(self):
        pix = QPixmap(self._iconSize)

        gradient = QLinearGradient(0, 0, 0, self._iconSize.height())
        gradient.setColorAt(0.0, QColor(240, 240, 240))
        gradient.setColorAt(1.0, QColor(224, 224, 224))

        brush = QBrush(gradient)

        curve_types = [(f"QEasingCurve.{e.name}", e) for e in QEasingCurve.Type if e.value <= 40]


        with QPainter(pix) as painter:

            for curve_name, curve_type in curve_types:
                painter.fillRect(QRect(QPoint(0, 0), self._iconSize), brush)
                curve = QEasingCurve(curve_type)

                painter.setPen(QColor(0, 0, 255, 64))
                x_axis = self._iconSize.height() / 1.5
                y_axis = self._iconSize.width() / 3.0
                painter.drawLine(0, x_axis, self._iconSize.width(), x_axis)
                painter.drawLine(y_axis, 0, y_axis, self._iconSize.height())

                curve_scale = self._iconSize.height() / 2.0

                painter.setPen(Qt.NoPen)

                # Start point.
                painter.setBrush(Qt.red)
                start = QPoint(y_axis,
                        x_axis - curve_scale * curve.valueForProgress(0))
                painter.drawRect(start.x() - 1, start.y() - 1, 3, 3)

                # End point.
                painter.setBrush(Qt.blue)
                end = QPoint(y_axis + curve_scale,
                        x_axis - curve_scale * curve.valueForProgress(1))
                painter.drawRect(end.x() - 1, end.y() - 1, 3, 3)

                curve_path = QPainterPath()
                curve_path.moveTo(QPointF(start))
                t = 0.0
                while t <= 1.0:
                    to = QPointF(y_axis + curve_scale * t,
                            x_axis - curve_scale * curve.valueForProgress(t))
                    curve_path.lineTo(to)
                    t += 1.0 / curve_scale

                painter.setRenderHint(QPainter.Antialiasing, True)
                painter.strokePath(curve_path, QColor(32, 32, 32))
                painter.setRenderHint(QPainter.Antialiasing, False)

                item = QListWidgetItem()
                item.setIcon(QIcon(pix))
                item.setText(curve_name)
                self._ui.easingCurvePicker.addItem(item)

    def start_animation(self):
        self._anim.setStartValue(QPointF(0, 0))
        self._anim.setEndValue(QPointF(100, 100))
        self._anim.setDuration(2000)
        self._anim.setLoopCount(-1)
        self._anim.start()

    def curve_changed(self, row):
        curve_type = QEasingCurve.Type(row)
        self._anim.setEasingCurve(curve_type)
        self._anim.setCurrentTime(0)

        is_elastic = (curve_type.value >= QEasingCurve.InElastic.value
                    and curve_type.value <= QEasingCurve.OutInElastic.value)
        is_bounce = (curve_type.value >= QEasingCurve.InBounce.value
                    and curve_type.value <= QEasingCurve.OutInBounce.value)

        self._ui.periodSpinBox.setEnabled(is_elastic)
        self._ui.amplitudeSpinBox.setEnabled(is_elastic or is_bounce)
        self._ui.overshootSpinBox.setEnabled(curve_type.value >= QEasingCurve.InBack.value
                                          and curve_type.value <= QEasingCurve.OutInBack.value)

    def path_changed(self, index):
        self._anim.set_path_type(index)

    def period_changed(self, value):
        curve = self._anim.easingCurve()
        curve.setPeriod(value)
        self._anim.setEasingCurve(curve)

    def amplitude_changed(self, value):
        curve = self._anim.easingCurve()
        curve.setAmplitude(value)
        self._anim.setEasingCurve(curve)

    def overshoot_changed(self, value):
        curve = self._anim.easingCurve()
        curve.setOvershoot(value)
        self._anim.setEasingCurve(curve)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Window()
    w.resize(600, 600)
    w.show()
    sys.exit(app.exec())
