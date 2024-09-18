# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the Callout example from Qt v5.x"""

import sys
from PySide6.QtWidgets import (QApplication, QGraphicsScene, QGraphicsView,
                               QGraphicsSimpleTextItem, QGraphicsItem)
from PySide6.QtCore import Qt, QPointF, QRectF, QRect
from PySide6.QtCharts import QChart, QLineSeries, QSplineSeries
from PySide6.QtGui import QPainter, QFont, QFontMetrics, QPainterPath, QColor


class Callout(QGraphicsItem):

    def __init__(self, chart):
        QGraphicsItem.__init__(self, chart)
        self._chart = chart
        self._text = ""
        self._textRect = QRectF()
        self._anchor = QPointF()
        self._font = QFont()
        self._rect = QRectF()

    def boundingRect(self):
        anchor = self.mapFromParent(self._chart.mapToPosition(self._anchor))
        rect = QRectF()
        rect.setLeft(min(self._rect.left(), anchor.x()))
        rect.setRight(max(self._rect.right(), anchor.x()))
        rect.setTop(min(self._rect.top(), anchor.y()))
        rect.setBottom(max(self._rect.bottom(), anchor.y()))

        return rect

    def paint(self, painter, option, widget):
        path = QPainterPath()
        path.addRoundedRect(self._rect, 5, 5)
        anchor = self.mapFromParent(self._chart.mapToPosition(self._anchor))
        if not self._rect.contains(anchor) and not self._anchor.isNull():
            point1 = QPointF()
            point2 = QPointF()

            # establish the position of the anchor point in relation to _rect
            above = anchor.y() <= self._rect.top()
            above_center = (anchor.y() > self._rect.top()
                            and anchor.y() <= self._rect.center().y())
            below_center = (anchor.y() > self._rect.center().y()
                            and anchor.y() <= self._rect.bottom())
            below = anchor.y() > self._rect.bottom()

            on_left = anchor.x() <= self._rect.left()
            left_of_center = (anchor.x() > self._rect.left()
                              and anchor.x() <= self._rect.center().x())
            right_of_center = (anchor.x() > self._rect.center().x()
                               and anchor.x() <= self._rect.right())
            on_right = anchor.x() > self._rect.right()

            # get the nearest _rect corner.
            x = (on_right + right_of_center) * self._rect.width()
            y = (below + below_center) * self._rect.height()
            corner_case = ((above and on_left) or (above and on_right)
                           or (below and on_left) or (below and on_right))
            vertical = abs(anchor.x() - x) > abs(anchor.y() - y)

            x1 = (x + left_of_center * 10 - right_of_center * 20 + corner_case
                  * int(not vertical) * (on_left * 10 - on_right * 20))
            y1 = (y + above_center * 10 - below_center * 20 + corner_case
                  * vertical * (above * 10 - below * 20))
            point1.setX(x1)
            point1.setY(y1)

            x2 = (x + left_of_center * 20 - right_of_center * 10 + corner_case
                  * int(not vertical) * (on_left * 20 - on_right * 10))
            y2 = (y + above_center * 20 - below_center * 10 + corner_case
                  * vertical * (above * 20 - below * 10))
            point2.setX(x2)
            point2.setY(y2)

            path.moveTo(point1)
            path.lineTo(anchor)
            path.lineTo(point2)
            path = path.simplified()

        painter.setBrush(QColor(255, 255, 255))
        painter.drawPath(path)
        painter.drawText(self._textRect, self._text)

    def mousePressEvent(self, event):
        event.setAccepted(True)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.setPos(self.mapToParent(
                event.pos() - event.buttonDownPos(Qt.LeftButton)))
            event.setAccepted(True)
        else:
            event.setAccepted(False)

    def set_text(self, text):
        self._text = text
        metrics = QFontMetrics(self._font)
        self._textRect = QRectF(metrics.boundingRect(
            QRect(0.0, 0.0, 150.0, 150.0), Qt.AlignLeft, self._text))
        self._textRect.translate(5, 5)
        self.prepareGeometryChange()
        self._rect = self._textRect.adjusted(-5, -5, 5, 5)

    def set_anchor(self, point):
        self._anchor = QPointF(point)

    def update_geometry(self):
        self.prepareGeometryChange()
        self.setPos(self._chart.mapToPosition(
            self._anchor) + QPointF(10, -50))


class View(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))

        self.setDragMode(QGraphicsView.NoDrag)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Chart
        self._chart = QChart()
        self._chart.setMinimumSize(640, 480)
        self._chart.setTitle("Hover the line to show callout. Click the line "
                             "to make it stay")
        self._chart.legend().hide()
        self.series = QLineSeries()
        self.series.append(1, 3)
        self.series.append(4, 5)
        self.series.append(5, 4.5)
        self.series.append(7, 1)
        self.series.append(11, 2)
        self._chart.addSeries(self.series)

        self.series2 = QSplineSeries()
        self.series2.append(1.6, 1.4)
        self.series2.append(2.4, 3.5)
        self.series2.append(3.7, 2.5)
        self.series2.append(7, 4)
        self.series2.append(10, 2)
        self._chart.addSeries(self.series2)

        self._chart.createDefaultAxes()
        self._chart.setAcceptHoverEvents(True)

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.scene().addItem(self._chart)

        self._coordX = QGraphicsSimpleTextItem(self._chart)
        self._coordX.setPos(
            self._chart.size().width() / 2 - 50, self._chart.size().height())
        self._coordX.setText("X: ")
        self._coordY = QGraphicsSimpleTextItem(self._chart)
        self._coordY.setPos(
            self._chart.size().width() / 2 + 50, self._chart.size().height())
        self._coordY.setText("Y: ")

        self._callouts = []
        self._tooltip = Callout(self._chart)

        self.series.clicked.connect(self.keep_callout)
        self.series.hovered.connect(self.tooltip)

        self.series2.clicked.connect(self.keep_callout)
        self.series2.hovered.connect(self.tooltip)

        self.setMouseTracking(True)

    def resizeEvent(self, event):
        if self.scene():
            self.scene().setSceneRect(QRectF(QPointF(0, 0), event.size()))
            self._chart.resize(event.size())
            self._coordX.setPos(
                self._chart.size().width() / 2 - 50,
                self._chart.size().height() - 20)
            self._coordY.setPos(
                self._chart.size().width() / 2 + 50,
                self._chart.size().height() - 20)
            for callout in self._callouts:
                callout.updateGeometry()
        QGraphicsView.resizeEvent(self, event)

    def mouseMoveEvent(self, event):
        pos = self._chart.mapToValue(event.position().toPoint())
        x = pos.x()
        y = pos.y()
        self._coordX.setText(f"X: {x:.2f}")
        self._coordY.setText(f"Y: {y:.2f}")
        QGraphicsView.mouseMoveEvent(self, event)

    def keep_callout(self):
        self._callouts.append(self._tooltip)
        self._tooltip = Callout(self._chart)

    def tooltip(self, point, state):
        if self._tooltip == 0:
            self._tooltip = Callout(self._chart)

        if state:
            x = point.x()
            y = point.y()
            self._tooltip.set_text(f"X: {x:.2f} \nY: {y:.2f} ")
            self._tooltip.set_anchor(point)
            self._tooltip.setZValue(11)
            self._tooltip.update_geometry()
            self._tooltip.show()
        else:
            self._tooltip.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    v = View()
    v.show()
    sys.exit(app.exec())
