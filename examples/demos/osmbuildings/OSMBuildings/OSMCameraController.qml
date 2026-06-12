// Copyright (C) 2024 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick3D

Item {
    id: root
    required property Node origin
    required property Camera camera

    property real xSpeed: 0.05
    property real ySpeed: 0.05

    property bool xInvert: false
    property bool yInvert: false

    property bool mouseEnabled: true
    property bool panEnabled: true

    readonly property bool inputsNeedProcessing: status.useMouse || status.isPanning

    readonly property real minimumZoom: 30
    readonly property real maximumZoom: 200

    readonly property real minimumTilt: 0
    readonly property real maximumTilt: 80

    implicitWidth: parent.width
    implicitHeight: parent.height

    Connections {
        target: root.camera
        Component.onCompleted: {
            onZChanged()
        }

        function onZChanged() {
            // Adjust near/far values based on distance
            let distance = root.camera.z
            if (distance < 1) {
                root.camera.clipNear = 0.01
                root.camera.clipFar = 100
            } else if (distance < 100) {
                root.camera.clipNear = 0.1
                root.camera.clipFar = 1000
            } else {
                root.camera.clipNear = 1
                root.camera.clipFar = 10000
            }
        }
    }

    DragHandler {
        id: dragHandler
        target: null
        enabled: root.mouseEnabled
        acceptedModifiers: Qt.NoModifier
        acceptedButtons: Qt.RightButton
        onCentroidChanged: {
            root.mouseMoved(Qt.vector2d(centroid.position.x, centroid.position.y), false);
        }

        onActiveChanged: {
            if (active)
                root.mousePressed(Qt.vector2d(centroid.position.x, centroid.position.y));
            else
                root.mouseReleased(Qt.vector2d(centroid.position.x, centroid.position.y));
        }
    }

    DragHandler {
        id: ctrlDragHandler
        target: null
        enabled: root.mouseEnabled && root.panEnabled
        //acceptedModifiers: Qt.ControlModifier
        onCentroidChanged: {
            root.panEvent(Qt.vector2d(centroid.position.x, centroid.position.y));
        }

        onActiveChanged: {
            if (active)
                root.startPan(Qt.vector2d(centroid.position.x, centroid.position.y));
            else
                root.endPan();
        }
    }

    PinchHandler {
        id: pinchHandler
        target: null
        enabled: root.mouseEnabled

        property real distance: 0.0
        onCentroidChanged: {
            root.panEvent(Qt.vector2d(centroid.position.x, centroid.position.y))
        }

        onActiveChanged: {
            if (active) {
                root.startPan(Qt.vector2d(centroid.position.x, centroid.position.y))
                distance = root.camera.z
            } else {
                root.endPan()
                distance = 0.0
            }
        }
        onScaleChanged: {

            root.camera.z = distance * (1 / scale)
            root.camera.z = Math.min(Math.max(root.camera.z, root.minimumZoom), root.maximumZoom)
        }
    }

    TapHandler {
        onTapped: root.forceActiveFocus()
    }

    WheelHandler {
        id: wheelHandler
        orientation: Qt.Vertical
        target: null
        enabled: root.mouseEnabled
        onWheel: event => {
            let delta = -event.angleDelta.y * 0.01;
            root.camera.z += root.camera.z * 0.1 * delta
            root.camera.z = Math.min(Math.max(root.camera.z, root.minimumZoom), root.maximumZoom)
        }
    }

    function mousePressed(newPos) {
        root.forceActiveFocus()
        status.currentPos = newPos
        status.lastPos = newPos
        status.useMouse = true;
    }

    function mouseReleased(newPos) {
        status.useMouse = false;
    }

    function mouseMoved(newPos: vector2d) {
        status.currentPos = newPos;
    }

    function startPan(pos: vector2d) {
        status.isPanning = true;
        status.currentPanPos = pos;
        status.lastPanPos = pos;
    }

    function endPan() {
        status.isPanning = false;
    }

    function panEvent(newPos: vector2d) {
        status.currentPanPos = newPos;
    }

    FrameAnimation {
        id: updateTimer
        running: root.inputsNeedProcessing
        onTriggered: status.processInput(frameTime * 100)
    }

    QtObject {
        id: status

        property bool useMouse: false
        property bool isPanning: false

        property vector2d lastPos: Qt.vector2d(0, 0)
        property vector2d lastPanPos: Qt.vector2d(0, 0)
        property vector2d currentPos: Qt.vector2d(0, 0)
        property vector2d currentPanPos: Qt.vector2d(0, 0)

        property real rotateAlongZ: 0
        property real rotateAlongXY: 50.0

        function processInput(frameDelta) {
            if (useMouse) {
                // Get the delta
                let delta = Qt.vector2d(lastPos.x - currentPos.x,
                                        lastPos.y - currentPos.y);

                let rotateX = delta.x * root.xSpeed * frameDelta
                if ( root.xInvert )
                    rotateX = -rotateX
                rotateAlongZ += rotateX;
                let rotateAlongZRad = rotateAlongZ * (Math.PI / 180.)

                root.origin.rotate(rotateX, Qt.vector3d(0.0, 0.0, -1.0), Node.SceneSpace)

                let rotateY = delta.y * -root.ySpeed * frameDelta
                if ( root.yInvert )
                    rotateY = -rotateY;

                let preRotateAlongXY = rotateAlongXY + rotateY
                if ( preRotateAlongXY <= root.maximumTilt && preRotateAlongXY >= root.minimumTilt )
                {
                    rotateAlongXY = preRotateAlongXY
                    root.origin.rotate(rotateY, Qt.vector3d(Math.cos(rotateAlongZRad), Math.sin(-rotateAlongZRad), 0.0), Node.SceneSpace)
                }

                lastPos = currentPos;
            }

            if (isPanning) {
                let delta = currentPanPos.minus(lastPanPos);
                delta.x = -delta.x

                delta.x = (delta.x / root.width) * root.camera.z * frameDelta
                delta.y = (delta.y / root.height) * root.camera.z * frameDelta

                let velocity = Qt.vector3d(0, 0, 0)
                // X Movement
                let xDirection = root.origin.right
                velocity = velocity.plus(Qt.vector3d(xDirection.x * delta.x,
                                                     xDirection.y * delta.x,
                                                     xDirection.z * delta.x));
                // Z Movement
                let zDirection = root.origin.right.crossProduct(Qt.vector3d(0.0, 0.0, -1.0))
                velocity = velocity.plus(Qt.vector3d(zDirection.x * delta.y,
                                                     zDirection.y * delta.y,
                                                     zDirection.z * delta.y));

                root.origin.position = root.origin.position.plus(velocity)

                lastPanPos = currentPanPos
            }
        }
    }

}
