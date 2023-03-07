// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick.Controls

Row {
    id: containerRow

    property var mapSource
    property real fontSize : 14
    property color labelBackground : "transparent"
    property int edge: Qt.RightEdge
    property alias expanded: sliderToggler.checked

    function rightEdge() {
        return (containerRow.edge === Qt.RightEdge);
    }

    layoutDirection: rightEdge() ? Qt.LeftToRight : Qt.RightToLeft
    anchors.top: parent.top
    anchors.bottom: parent.bottom
    anchors.right: rightEdge() ? parent.right : undefined
    anchors.left: rightEdge() ? undefined : parent.left

    AbstractButton {
        id: sliderToggler
        width: 32
        height: 96
        checkable: true
        checked: true
        anchors.verticalCenter: parent.verticalCenter

        transform:  Scale {
                        origin.x: rightEdge() ? 0 : sliderToggler.width / 2
                        xScale: rightEdge() ? 1 : -1
                    }

        background: Rectangle {
            color: "transparent"
        }


        property real shear: 0.333
        property real buttonOpacity: 0.5
        property real mirror : rightEdge() ? 1.0 : -1.0

        Rectangle {
            width: 16
            height: 48
            color: "seagreen"
            antialiasing: true
            opacity: sliderToggler.buttonOpacity
            anchors.top: parent.top
            anchors.left: sliderToggler.checked ?  parent.left : parent.horizontalCenter
            transform: Matrix4x4 {
                property real d : sliderToggler.checked ? 1.0 : -1.0
                matrix:    Qt.matrix4x4(1.0,  d * sliderToggler.shear,    0.0,    0.0,
                                        0.0,    1.0,    0.0,    0.0,
                                        0.0,    0.0,    1.0,    0.0,
                                        0.0,    0.0,    0.0,    1.0)
            }
        }

        Rectangle {
            width: 16
            height: 48
            color: "seagreen"
            antialiasing: true
            opacity: sliderToggler.buttonOpacity
            anchors.top: parent.verticalCenter
            anchors.right: sliderToggler.checked ?  parent.right : parent.horizontalCenter
            transform: Matrix4x4 {
                property real d : sliderToggler.checked ? -1.0 : 1.0
                matrix:    Qt.matrix4x4(1.0,  d * sliderToggler.shear,    0.0,    0.0,
                                        0.0,    1.0,    0.0,    0.0,
                                        0.0,    0.0,    1.0,    0.0,
                                        0.0,    0.0,    0.0,    1.0)
            }
        }
    }

    Rectangle {
        id: sliderContainer
        height: parent.height
        width: sliderRow.width + 10
        visible: sliderToggler.checked
        color: Qt.rgba( 0, 191 / 255.0, 255 / 255.0, 0.07)

        property var labelBorderColor: "transparent"
        property var slidersHeight : sliderContainer.height
                                     - rowSliderValues.height
                                     - rowSliderLabels.height
                                     - sliderColumn.spacing * 2
                                     - sliderColumn.topPadding
                                     - sliderColumn.bottomPadding

        Column {
            id: sliderColumn
            spacing: 10
            topPadding: 16
            bottomPadding: 48
            anchors.centerIn: parent

            // the sliders value labels
            Row {
                id: rowSliderValues
                spacing: sliderRow.spacing
                width: sliderRow.width
                height: 32
                property real entryWidth: zoomSlider.width

                Rectangle{
                    color: labelBackground
                    height: parent.height
                    width: parent.entryWidth
                    border.color: sliderContainer.labelBorderColor
                    Label {
                        id: labelZoomValue
                        text: zoomSlider.value.toFixed(3)
                        font.pixelSize: fontSize
                        rotation: -90
                        anchors.centerIn: parent
                    }
                }
                Rectangle{
                    color: labelBackground
                    height: parent.height
                    width: parent.entryWidth
                    border.color: sliderContainer.labelBorderColor
                    Label {
                        id: labelBearingValue
                        text: bearingSlider.value.toFixed(2)
                        font.pixelSize: fontSize
                        rotation: -90
                        anchors.centerIn: parent
                    }
                }
                Rectangle{
                    color: labelBackground
                    height: parent.height
                    width: parent.entryWidth
                    border.color: sliderContainer.labelBorderColor
                    Label {
                        id: labelTiltValue
                        text: tiltSlider.value.toFixed(2)
                        font.pixelSize: fontSize
                        rotation: -90
                        anchors.centerIn: parent
                    }
                }
                Rectangle{
                    color: labelBackground
                    height: parent.height
                    width: parent.entryWidth
                    border.color: sliderContainer.labelBorderColor
                    Label {
                        id: labelFovValue
                        text: fovSlider.value.toFixed(2)
                        font.pixelSize: fontSize
                        rotation: -90
                        anchors.centerIn: parent
                    }
                }
            } // rowSliderValues

            // The sliders row
            Row {
                id: sliderRow
                height: sliderContainer.slidersHeight

                Slider {
                    id: zoomSlider
                    height: parent.height
                    orientation : Qt.Vertical
                    from : containerRow.mapSource.minimumZoomLevel
                    to : containerRow.mapSource.maximumZoomLevel
                    value : containerRow.mapSource.zoomLevel
                    onValueChanged: {
                            containerRow.mapSource.zoomLevel = value
                    }
                }
                Slider {
                    id: bearingSlider
                    height: parent.height
                    from: 0
                    to: 360
                    orientation : Qt.Vertical
                    value: containerRow.mapSource.bearing
                    onValueChanged: {
                        containerRow.mapSource.bearing = value;
                    }
                }
                Slider {
                    id: tiltSlider
                    height: parent.height
                    orientation : Qt.Vertical
                    from: containerRow.mapSource.minimumTilt;
                    to: containerRow.mapSource.maximumTilt
                    value: containerRow.mapSource.tilt
                    onValueChanged: {
                        containerRow.mapSource.tilt = value;
                    }
                }
                Slider {
                    id: fovSlider
                    height: parent.height
                    orientation : Qt.Vertical
                    from: containerRow.mapSource.minimumFieldOfView
                    to: containerRow.mapSource.maximumFieldOfView
                    value: containerRow.mapSource.fieldOfView
                    onValueChanged: {
                        containerRow.mapSource.fieldOfView = value;
                    }
                }
            } // Row sliders

            // The labels row
            Row {
                id: rowSliderLabels
                spacing: sliderRow.spacing
                width: sliderRow.width
                property real entryWidth: zoomSlider.width
                property real entryHeight: 64

                Rectangle{
                    color: labelBackground
                    height: parent.entryHeight
                    width: parent.entryWidth
                    border.color: sliderContainer.labelBorderColor
                    Label {
                        id: labelZoom
                        text: "Zoom"
                        font.pixelSize: fontSize
                        rotation: -90
                        anchors.centerIn: parent
                    }
                }

                Rectangle{
                    color: labelBackground
                    height: parent.entryHeight
                    width: parent.entryWidth
                    border.color: sliderContainer.labelBorderColor
                    Label {
                        id: labelBearing
                        text: "Bearing"
                        font.pixelSize: fontSize
                        rotation: -90
                        anchors.centerIn: parent
                    }
                }
                Rectangle{
                    color: labelBackground
                    height: parent.entryHeight
                    width: parent.entryWidth
                    border.color: sliderContainer.labelBorderColor
                    Label {
                        id: labelTilt
                        text: "Tilt"
                        font.pixelSize: fontSize
                        rotation: -90
                        anchors.centerIn: parent
                    }
                }
                Rectangle{
                    color: labelBackground
                    height: parent.entryHeight
                    width: parent.entryWidth
                    border.color: sliderContainer.labelBorderColor
                    Label {
                        id: labelFov
                        text: "FoV"
                        font.pixelSize: fontSize
                        rotation: -90
                        anchors.centerIn: parent
                    }
                }
            } // rowSliderLabels
        } // Column
    } // sliderContainer
} // containerRow
