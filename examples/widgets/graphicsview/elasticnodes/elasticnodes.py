
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

import sys
import weakref
import math
from PySide6 import QtCore, QtGui, QtWidgets


def random(boundary):
    return QtCore.QRandomGenerator.global_().bounded(boundary)


class Edge(QtWidgets.QGraphicsItem):
    Pi = math.pi
    two_pi = 2.0 * Pi

    type = QtWidgets.QGraphicsItem.UserType + 2

    def __init__(self, sourceNode, destNode):
        QtWidgets.QGraphicsItem.__init__(self)

        self._arrow_size = 10.0
        self._source_point = QtCore.QPointF()
        self._dest_point = QtCore.QPointF()
        self.setAcceptedMouseButtons(QtCore.Qt.NoButton)
        self.source = weakref.ref(sourceNode)
        self.dest = weakref.ref(destNode)
        self.source().add_edge(self)
        self.dest().add_edge(self)
        self.adjust()

    def type(self):
        return Edge.type

    def source_node(self):
        return self.source()

    def set_source_node(self, node):
        self.source = weakref.ref(node)
        self.adjust()

    def dest_node(self):
        return self.dest()

    def set_dest_node(self, node):
        self.dest = weakref.ref(node)
        self.adjust()

    def adjust(self):
        if not self.source() or not self.dest():
            return

        line = QtCore.QLineF(self.mapFromItem(self.source(), 0, 0), self.mapFromItem(self.dest(), 0, 0))
        length = line.length()

        if length == 0.0:
            return

        edge_offset = QtCore.QPointF((line.dx() * 10) / length, (line.dy() * 10) / length)

        self.prepareGeometryChange()
        self._source_point = line.p1() + edge_offset
        self._dest_point = line.p2() - edge_offset

    def boundingRect(self):
        if not self.source() or not self.dest():
            return QtCore.QRectF()

        pen_width = 1
        extra = (pen_width + self._arrow_size) / 2.0

        return QtCore.QRectF(self._source_point,
                             QtCore.QSizeF(self._dest_point.x() - self._source_point.x(),
                                           self._dest_point.y() - self._source_point.y())).normalized().adjusted(-extra, -extra, extra, extra)

    def paint(self, painter, option, widget):
        if not self.source() or not self.dest():
            return

        # Draw the line itself.
        line = QtCore.QLineF(self._source_point, self._dest_point)

        if line.length() == 0.0:
            return

        painter.setPen(QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        painter.drawLine(line)

        # Draw the arrows if there's enough room.
        angle = math.acos(line.dx() / line.length())
        if line.dy() >= 0:
            angle = Edge.two_pi - angle

        source_arrow_p1 = self._source_point + QtCore.QPointF(math.sin(angle + Edge.Pi / 3) * self._arrow_size,
                                                          math.cos(angle + Edge.Pi / 3) * self._arrow_size)
        source_arrow_p2 = self._source_point + QtCore.QPointF(math.sin(angle + Edge.Pi - Edge.Pi / 3) * self._arrow_size,
                                                          math.cos(angle + Edge.Pi - Edge.Pi / 3) * self._arrow_size)
        dest_arrow_p1 = self._dest_point + QtCore.QPointF(math.sin(angle - Edge.Pi / 3) * self._arrow_size,
                                                      math.cos(angle - Edge.Pi / 3) * self._arrow_size)
        dest_arrow_p2 = self._dest_point + QtCore.QPointF(math.sin(angle - Edge.Pi + Edge.Pi / 3) * self._arrow_size,
                                                      math.cos(angle - Edge.Pi + Edge.Pi / 3) * self._arrow_size)

        painter.setBrush(QtCore.Qt.black)
        painter.drawPolygon(QtGui.QPolygonF([line.p1(), source_arrow_p1, source_arrow_p2]))
        painter.drawPolygon(QtGui.QPolygonF([line.p2(), dest_arrow_p1, dest_arrow_p2]))


class Node(QtWidgets.QGraphicsItem):
    type = QtWidgets.QGraphicsItem.UserType + 1

    def __init__(self, graphWidget):
        QtWidgets.QGraphicsItem.__init__(self)

        self.graph = weakref.ref(graphWidget)
        self._edge_list = []
        self._new_pos = QtCore.QPointF()
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(self.DeviceCoordinateCache)
        self.setZValue(-1)

    def type(self):
        return Node.type

    def add_edge(self, edge):
        self._edge_list.append(weakref.ref(edge))
        edge.adjust()

    def edges(self):
        return self._edge_list

    def calculate_forces(self):
        if not self.scene() or self.scene().mouseGrabberItem() is self:
            self._new_pos = self.pos()
            return

        # Sum up all forces pushing this item away.
        xvel = 0.0
        yvel = 0.0
        for item in self.scene().items():
            if not isinstance(item, Node):
                continue

            line = QtCore.QLineF(self.mapFromItem(item, 0, 0), QtCore.QPointF(0, 0))
            dx = line.dx()
            dy = line.dy()
            l = 2.0 * (dx * dx + dy * dy)
            if l > 0:
                xvel += (dx * 150.0) / l
                yvel += (dy * 150.0) / l

        # Now subtract all forces pulling items together.
        weight = (len(self._edge_list) + 1) * 10.0
        for edge in self._edge_list:
            if edge().source_node() is self:
                pos = self.mapFromItem(edge().dest_node(), 0, 0)
            else:
                pos = self.mapFromItem(edge().source_node(), 0, 0)
            xvel += pos.x() / weight
            yvel += pos.y() / weight

        if QtCore.qAbs(xvel) < 0.1 and QtCore.qAbs(yvel) < 0.1:
            xvel = yvel = 0.0

        scene_rect = self.scene().sceneRect()
        self._new_pos = self.pos() + QtCore.QPointF(xvel, yvel)
        self._new_pos.setX(min(max(self._new_pos.x(), scene_rect.left() + 10), scene_rect.right() - 10))
        self._new_pos.setY(min(max(self._new_pos.y(), scene_rect.top() + 10), scene_rect.bottom() - 10))

    def advance(self):
        if self._new_pos == self.pos():
            return False

        self.setPos(self._new_pos)
        return True

    def boundingRect(self):
        adjust = 2.0
        return QtCore.QRectF(-10 - adjust, -10 - adjust,
                             23 + adjust, 23 + adjust)

    def shape(self):
        path = QtGui.QPainterPath()
        path.addEllipse(-10, -10, 20, 20)
        return path

    def paint(self, painter, option, widget):
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtCore.Qt.darkGray)
        painter.drawEllipse(-7, -7, 20, 20)

        gradient = QtGui.QRadialGradient(-3, -3, 10)
        if option.state & QtWidgets.QStyle.State_Sunken:
            gradient.setCenter(3, 3)
            gradient.setFocalPoint(3, 3)
            gradient.setColorAt(1, QtGui.QColor(QtCore.Qt.yellow).lighter(120))
            gradient.setColorAt(0, QtGui.QColor(QtCore.Qt.darkYellow).lighter(120))
        else:
            gradient.setColorAt(0, QtCore.Qt.yellow)
            gradient.setColorAt(1, QtCore.Qt.darkYellow)

        painter.setBrush(QtGui.QBrush(gradient))
        painter.setPen(QtGui.QPen(QtCore.Qt.black, 0))
        painter.drawEllipse(-10, -10, 20, 20)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionChange:
            for edge in self._edge_list:
                edge().adjust()
            self.graph().item_moved()

        return QtWidgets.QGraphicsItem.itemChange(self, change, value)

    def mousePressEvent(self, event):
        self.update()
        QtWidgets.QGraphicsItem.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        self.update()
        QtWidgets.QGraphicsItem.mouseReleaseEvent(self, event)


class GraphWidget(QtWidgets.QGraphicsView):
    def __init__(self):
        QtWidgets.QGraphicsView.__init__(self)

        self._timer_id = 0

        scene = QtWidgets.QGraphicsScene(self)
        scene.setItemIndexMethod(QtWidgets.QGraphicsScene.NoIndex)
        scene.setSceneRect(-200, -200, 400, 400)
        self.setScene(scene)
        self.setCacheMode(QtWidgets.QGraphicsView.CacheBackground)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorViewCenter)

        node1 = Node(self)
        node2 = Node(self)
        node3 = Node(self)
        node4 = Node(self)
        self._center_node = Node(self)
        node6 = Node(self)
        node7 = Node(self)
        node8 = Node(self)
        node9 = Node(self)
        scene.addItem(node1)
        scene.addItem(node2)
        scene.addItem(node3)
        scene.addItem(node4)
        scene.addItem(self._center_node)
        scene.addItem(node6)
        scene.addItem(node7)
        scene.addItem(node8)
        scene.addItem(node9)
        scene.addItem(Edge(node1, node2))
        scene.addItem(Edge(node2, node3))
        scene.addItem(Edge(node2, self._center_node))
        scene.addItem(Edge(node3, node6))
        scene.addItem(Edge(node4, node1))
        scene.addItem(Edge(node4, self._center_node))
        scene.addItem(Edge(self._center_node, node6))
        scene.addItem(Edge(self._center_node, node8))
        scene.addItem(Edge(node6, node9))
        scene.addItem(Edge(node7, node4))
        scene.addItem(Edge(node8, node7))
        scene.addItem(Edge(node9, node8))

        node1.setPos(-50, -50)
        node2.setPos(0, -50)
        node3.setPos(50, -50)
        node4.setPos(-50, 0)
        self._center_node.setPos(0, 0)
        node6.setPos(50, 0)
        node7.setPos(-50, 50)
        node8.setPos(0, 50)
        node9.setPos(50, 50)

        self.scale(0.8, 0.8)
        self.setMinimumSize(400, 400)
        self.setWindowTitle(self.tr("Elastic Nodes"))

    def item_moved(self):
        if not self._timer_id:
            self._timer_id = self.startTimer(1000 / 25)

    def keyPressEvent(self, event):
        key = event.key()

        if key == QtCore.Qt.Key_Up:
            self._center_node.moveBy(0, -20)
        elif key == QtCore.Qt.Key_Down:
            self._center_node.moveBy(0, 20)
        elif key == QtCore.Qt.Key_Left:
            self._center_node.moveBy(-20, 0)
        elif key == QtCore.Qt.Key_Right:
            self._center_node.moveBy(20, 0)
        elif key == QtCore.Qt.Key_Plus:
            self.scale_view(1.2)
        elif key == QtCore.Qt.Key_Minus:
            self.scale_view(1 / 1.2)
        elif key == QtCore.Qt.Key_Space or key == QtCore.Qt.Key_Enter:
            for item in self.scene().items():
                if isinstance(item, Node):
                    item.setPos(-150 + random(300), -150 + random(300))
        else:
            QtWidgets.QGraphicsView.keyPressEvent(self, event)


    def timerEvent(self, event):
        nodes = [item for item in self.scene().items() if isinstance(item, Node)]

        for node in nodes:
            node.calculate_forces()

        items_moved = False
        for node in nodes:
            if node.advance():
                items_moved = True

        if not items_moved:
            self.killTimer(self._timer_id)
            self._timer_id = 0

    def wheelEvent(self, event):
        self.scale_view(math.pow(2.0, -event.delta() / 240.0))

    def draw_background(self, painter, rect):
        # Shadow.
        scene_rect = self.sceneRect()
        right_shadow = QtCore.QRectF(scene_rect.right(), scene_rect.top() + 5, 5, scene_rect.height())
        bottom_shadow = QtCore.QRectF(scene_rect.left() + 5, scene_rect.bottom(), scene_rect.width(), 5)
        if right_shadow.intersects(rect) or right_shadow.contains(rect):
                painter.fillRect(right_shadow, QtCore.Qt.darkGray)
        if bottom_shadow.intersects(rect) or bottom_shadow.contains(rect):
                painter.fillRect(bottom_shadow, QtCore.Qt.darkGray)

        # Fill.
        gradient = QtGui.QLinearGradient(scene_rect.topLeft(), scene_rect.bottomRight())
        gradient.setColorAt(0, QtCore.Qt.white)
        gradient.setColorAt(1, QtCore.Qt.lightGray)
        painter.fillRect(rect.intersected(scene_rect), QtGui.QBrush(gradient))
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawRect(scene_rect)

        # Text.
        text_rect = QtCore.QRectF(scene_rect.left() + 4, scene_rect.top() + 4,
                                 scene_rect.width() - 4, scene_rect.height() - 4)
        message = self.tr("Click and drag the nodes around, and zoom with the "
                          "mouse wheel or the '+' and '-' keys")

        font = painter.font()
        font.setBold(True)
        font.setPointSize(14)
        painter.setFont(font)
        painter.setPen(QtCore.Qt.lightGray)
        painter.drawText(text_rect.translated(2, 2), message)
        painter.setPen(QtCore.Qt.black)
        painter.drawText(text_rect, message)

    def scale_view(self, scaleFactor):
        factor = self.matrix().scale(scaleFactor, scaleFactor).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()

        if factor < 0.07 or factor > 100:
            return

        self.scale(scaleFactor, scaleFactor)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    widget = GraphWidget()
    widget.show()

    sys.exit(app.exec_())
