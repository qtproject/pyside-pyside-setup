// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick.Controls
import QtDataVisualization

Rectangle {
    id: spectrogramView
    color: surfaceGraph.theme.windowColor

    required property bool portraitMode

    property real buttonWidth: spectrogramView.portraitMode ? (spectrogramView.width - 35) / 2
                                                            : (spectrogramView.width - 50) / 5

    SpectrogramData {
        id: surfaceData
    }

    Item {
        id: surfaceView
        anchors.top: buttons.bottom
        anchors.left: parent.left
        anchors.right: legend.left
        anchors.bottom: parent.bottom

        ColorGradient {
            id: surfaceGradient
            ColorGradientStop { position: 0.0; color: "black" }
            ColorGradientStop { position: 0.2; color: "red" }
            ColorGradientStop { position: 0.5; color: "blue" }
            ColorGradientStop { position: 0.8; color: "yellow" }
            ColorGradientStop { position: 1.0; color: "white" }
        }

        ValueAxis3D {
            id: xAxis
            segmentCount: 8
            labelFormat: "%i\u00B0"
            title: "Angle"
            titleVisible: true
            titleFixed: false
        }

        ValueAxis3D {
            id: yAxis
            segmentCount: 8
            labelFormat: "%i \%"
            title: "Value"
            titleVisible: true
            labelAutoRotation: 0
            titleFixed: false
        }

        ValueAxis3D {
            id: zAxis
            segmentCount: 5
            labelFormat: "%i nm"
            title: "Radius"
            titleVisible: true
            titleFixed: false
        }

        Theme3D {
            id: customTheme
            type: Theme3D.ThemeQt
            // Don't show specular spotlight as we don't want it to distort the colors
            lightStrength: 0.0
            ambientLightStrength: 1.0
            backgroundEnabled: false
            gridLineColor: "#AAAAAA"
            windowColor: "#EEEEEE"
        }

        //! [0]
        Surface3D {
            id: surfaceGraph
            anchors.fill: parent

            Surface3DSeries {
                id: surfaceSeries
                flatShadingEnabled: false
                drawMode: Surface3DSeries.DrawSurface
                baseGradient: surfaceGradient
                colorStyle: Theme3D.ColorStyleRangeGradient
                itemLabelFormat: "(@xLabel, @zLabel): @yLabel"

                ItemModelSurfaceDataProxy {
                    itemModel: surfaceData.model
                    rowRole: "radius"
                    columnRole: "angle"
                    yPosRole: "value"
                }
            }
            //! [0]

            //! [1]
            // Remove the perspective and view the graph from top down to achieve 2D effect
            orthoProjection: true
            scene.activeCamera.cameraPreset: Camera3D.CameraPresetDirectlyAbove
            //! [1]

            //! [2]
            flipHorizontalGrid: true
            //! [2]

            //! [4]
            radialLabelOffset: 0.01
            //! [4]

            //! [5]
            inputHandler: TouchInputHandler3D {
                rotationEnabled: !surfaceGraph.orthoProjection
            }
            //! [5]

            theme: customTheme
            shadowQuality: AbstractGraph3D.ShadowQualityNone
            selectionMode: AbstractGraph3D.SelectionSlice | AbstractGraph3D.SelectionItemAndColumn
            axisX: xAxis
            axisY: yAxis
            axisZ: zAxis

            aspectRatio: 1.0
            horizontalAspectRatio: 1.0
            scene.activeCamera.zoomLevel: 140
        }
    }

    Item {
        id: buttons
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: spectrogramView.portraitMode ? (polarToggle.height + 10) * 3
                                             : polarToggle.height + 30
        anchors.margins: 10

        //! [3]
        Button {
            id: polarToggle
            anchors.margins: 5
            anchors.left: parent.left
            anchors.top: parent.top
            width: spectrogramView.buttonWidth // Calculated elsewhere based on screen orientation
            text: "Switch to\n" + (surfaceGraph.polar ? "cartesian" : "polar")
            onClicked: surfaceGraph.polar = !surfaceGraph.polar;
        }
        //! [3]

        Button {
            id: orthoToggle
            anchors.margins: 5
            anchors.left: polarToggle.right
            anchors.top: parent.top
            width: spectrogramView.buttonWidth
            text: "Switch to\n" + (surfaceGraph.orthoProjection ? "perspective" : "orthographic")
            onClicked: {
                if (surfaceGraph.orthoProjection) {
                    surfaceGraph.orthoProjection = false;
                    xAxis.labelAutoRotation = 30;
                    yAxis.labelAutoRotation = 30;
                    zAxis.labelAutoRotation = 30;
                } else {
                    surfaceGraph.orthoProjection = true;
                    surfaceGraph.scene.activeCamera.cameraPreset
                            = Camera3D.CameraPresetDirectlyAbove;
                    surfaceSeries.drawMode &= ~Surface3DSeries.DrawWireframe;
                    xAxis.labelAutoRotation = 0;
                    yAxis.labelAutoRotation = 0;
                    zAxis.labelAutoRotation = 0;
                }
            }
        }

        Button {
            id: flipGridToggle
            anchors.margins: 5
            anchors.left: spectrogramView.portraitMode ? parent.left : orthoToggle.right
            anchors.top: spectrogramView.portraitMode ? orthoToggle.bottom : parent.top
            width: spectrogramView.buttonWidth
            text: "Toggle axis\ngrid on top"
            onClicked: surfaceGraph.flipHorizontalGrid = !surfaceGraph.flipHorizontalGrid;
        }

        Button {
            id: labelOffsetToggle
            anchors.margins: 5
            anchors.left: flipGridToggle.right
            anchors.top: spectrogramView.portraitMode ? orthoToggle.bottom : parent.top
            width: spectrogramView.buttonWidth
            text: "Toggle radial\nlabel position"
            visible: surfaceGraph.polar
            onClicked: {
                if (surfaceGraph.radialLabelOffset >= 1.0)
                    surfaceGraph.radialLabelOffset = 0.01;
                else
                    surfaceGraph.radialLabelOffset = 1.0;
            }
        }

        Button {
            id: surfaceGridToggle
            anchors.margins: 5
            anchors.left: spectrogramView.portraitMode ? (labelOffsetToggle.visible ? parent.left
                                                                                    : flipGridToggle.right)
                                                       : (labelOffsetToggle.visible ? labelOffsetToggle.right
                                                                                    : flipGridToggle.right)
            anchors.top: spectrogramView.portraitMode ? (labelOffsetToggle.visible ? labelOffsetToggle.bottom
                                                                                   : orthoToggle.bottom)
                                                      : parent.top
            width: spectrogramView.buttonWidth
            text: "Toggle\nsurface grid"
            visible: !surfaceGraph.orthoProjection
            onClicked: {
                if (surfaceSeries.drawMode & Surface3DSeries.DrawWireframe)
                    surfaceSeries.drawMode &= ~Surface3DSeries.DrawWireframe;
                else
                    surfaceSeries.drawMode |= Surface3DSeries.DrawWireframe;
            }
        }
    }

    Item {
        id: legend
        anchors.bottom: parent.bottom
        anchors.top: buttons.bottom
        anchors.right: parent.right
        width: spectrogramView.portraitMode ? 100 : 125

        Rectangle {
            id: gradient
            anchors.margins: 20
            anchors.bottom: legend.bottom
            anchors.top: legend.top
            anchors.right: legend.right
            border.color: "black"
            border.width: 1
            width: spectrogramView.portraitMode ? 25 : 50
            rotation: 180
            gradient: Gradient {
                GradientStop { position: 0.0; color: "black" }
                GradientStop { position: 0.2; color: "red" }
                GradientStop { position: 0.5; color: "blue" }
                GradientStop { position: 0.8; color: "yellow" }
                GradientStop { position: 1.0; color: "white" }
            }
        }

        Text {
            anchors.verticalCenter: gradient.bottom
            anchors.right: gradient.left
            anchors.margins: 2
            text: surfaceGraph.axisY.min  + "%"
        }

        Text {
            anchors.verticalCenter: gradient.verticalCenter
            anchors.right: gradient.left
            anchors.margins: 2
            text: (surfaceGraph.axisY.max + surfaceGraph.axisY.min) / 2  + "%"
        }

        Text {
            anchors.verticalCenter: gradient.top
            anchors.right: gradient.left
            anchors.margins: 2
            text: surfaceGraph.axisY.max + "%"
        }
    }
}
