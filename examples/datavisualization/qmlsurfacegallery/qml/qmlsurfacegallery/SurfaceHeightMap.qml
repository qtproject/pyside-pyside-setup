// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick.Controls
import QtDataVisualization

Rectangle {
    id: heightMapView
    color: surfacePlot.theme.windowColor

    required property bool portraitMode

    property real buttonWidth: heightMapView.portraitMode ? (heightMapView.width - 35) / 2
                                                          : (heightMapView.width - 40) / 3

    Item {
        id: surfaceView
        anchors.top: buttons.bottom
        anchors.bottom: heightMapView.bottom
        anchors.left: heightMapView.left
        anchors.right: heightMapView.right

        //! [1]
        ColorGradient {
            id: surfaceGradient
            ColorGradientStop { position: 0.0; color: "darkgreen"}
            ColorGradientStop { position: 0.15; color: "darkslategray" }
            ColorGradientStop { position: 0.7; color: "peru" }
            ColorGradientStop { position: 1.0; color: "white" }
        }
        //! [1]

        Surface3D {
            id: surfacePlot
            width: surfaceView.width
            height: surfaceView.height
            aspectRatio: 3.0
            //! [2]
            theme: Theme3D {
                type: Theme3D.ThemeStoneMoss
                font.family: "STCaiyun"
                font.pointSize: 35
                colorStyle: Theme3D.ColorStyleRangeGradient
                baseGradients: [surfaceGradient] // Use the custom gradient
            }
            //! [2]
            shadowQuality: AbstractGraph3D.ShadowQualityMedium
            selectionMode: AbstractGraph3D.SelectionSlice | AbstractGraph3D.SelectionItemAndRow
            scene.activeCamera.cameraPreset: Camera3D.CameraPresetIsometricLeft
            axisX.segmentCount: 3
            axisX.subSegmentCount: 3
            axisX.labelFormat: "%i"
            axisZ.segmentCount: 3
            axisZ.subSegmentCount: 3
            axisZ.labelFormat: "%i"
            axisY.segmentCount: 2
            axisY.subSegmentCount: 2
            axisY.labelFormat: "%i"
            axisY.title: "Height (m)"
            axisX.title: "Longitude 175.x\"E"
            axisZ.title: "Latitude -39.x\"N"
            axisY.titleVisible: true
            axisX.titleVisible: true
            axisZ.titleVisible: true

            //! [0]
            Surface3DSeries {
                id: heightSeries
                flatShadingEnabled: false
                drawMode: Surface3DSeries.DrawSurface

                HeightMapSurfaceDataProxy {
                    heightMapFile: ":/qml/qmlsurfacegallery/heightmap.png"
                    // We don't want the default data values set by heightmap proxy, but use
                    // actual coordinate and height values instead
                    autoScaleY: true
                    minYValue: 740
                    maxYValue: 2787
                    minZValue: -374 // ~ -39.374411"N
                    maxZValue: -116 // ~ -39.115971"N
                    minXValue: 472  // ~ 175.471767"E
                    maxXValue: 781  // ~ 175.780758"E
                }

                onDrawModeChanged: heightMapView.checkState()
            }
            //! [0]
        }
    }

    Item {
        id: buttons
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: 10
        height: heightMapView.portraitMode ? surfaceGridToggle.implicitHeight * 3 + 20
                                           : surfaceGridToggle.implicitHeight * 2 + 15
        opacity: 0.5

        Button {
            id: surfaceGridToggle
            anchors.margins: 5
            anchors.left: parent.left
            anchors.top: parent.top
            width: heightMapView.buttonWidth // Calculated elsewhere based on screen orientation
            text: "Show Surface\nGrid"
            //! [3]
            onClicked: {
                if (heightSeries.drawMode & Surface3DSeries.DrawWireframe)
                    heightSeries.drawMode &= ~Surface3DSeries.DrawWireframe;
                else
                    heightSeries.drawMode |= Surface3DSeries.DrawWireframe;
            }
            //! [3]
        }

        Button {
            id: surfaceGridColor
            anchors.margins: 5
            anchors.left: surfaceGridToggle.right
            anchors.top: parent.top
            width: heightMapView.buttonWidth
            text: "Red surface\ngrid color"
            //! [4]
            onClicked: {
                if (Qt.colorEqual(heightSeries.wireframeColor, "#000000")) {
                    heightSeries.wireframeColor = "red";
                    text = "Black surface\ngrid color";
                } else {
                    heightSeries.wireframeColor = "black";
                    text = "Red surface\ngrid color";
                }
            }
            //! [4]
        }

        Button {
            id: surfaceToggle
            anchors.margins: 5
            anchors.left: heightMapView.portraitMode ? parent.left : surfaceGridColor.right
            anchors.top: heightMapView.portraitMode ? surfaceGridColor.bottom : parent.top
            width: heightMapView.buttonWidth
            text: "Hide\nSurface"
            //! [5]
            onClicked: {
                if (heightSeries.drawMode & Surface3DSeries.DrawSurface)
                    heightSeries.drawMode &= ~Surface3DSeries.DrawSurface;
                else
                    heightSeries.drawMode |= Surface3DSeries.DrawSurface;
            }
            //! [5]
        }

        Button {
            id: flatShadingToggle
            anchors.margins: 5
            anchors.left: heightMapView.portraitMode ? surfaceToggle.right : parent.left
            anchors.top: heightMapView.portraitMode ? surfaceGridColor.bottom : surfaceToggle.bottom
            width: heightMapView.buttonWidth
            text: heightSeries.flatShadingSupported ? "Show\nFlat" : "Flat not\nsupported"
            enabled: heightSeries.flatShadingSupported
            //! [6]
            onClicked: {
                if (heightSeries.flatShadingEnabled) {
                    heightSeries.flatShadingEnabled = false;
                    text = "Show\nFlat"
                } else {
                    heightSeries.flatShadingEnabled = true;
                    text = "Show\nSmooth"
                }
            }
            //! [6]
        }

        Button {
            id: backgroundToggle
            anchors.margins: 5
            anchors.left: heightMapView.portraitMode ? parent.left : flatShadingToggle.right
            anchors.top: heightMapView.portraitMode ? flatShadingToggle.bottom
                                                    : surfaceToggle.bottom
            width: heightMapView.buttonWidth
            text: "Hide\nBackground"
            onClicked: {
                if (surfacePlot.theme.backgroundEnabled) {
                    surfacePlot.theme.backgroundEnabled = false;
                    text = "Show\nBackground";
                } else {
                    surfacePlot.theme.backgroundEnabled = true;
                    text = "Hide\nBackground";
                }
            }
        }

        Button {
            id: gridToggle
            anchors.margins: 5
            anchors.left: backgroundToggle.right
            anchors.top: heightMapView.portraitMode ? flatShadingToggle.bottom
                                                    : surfaceToggle.bottom
            width: heightMapView.buttonWidth
            text: "Hide\nGrid"
            onClicked: {
                if (surfacePlot.theme.gridEnabled) {
                    surfacePlot.theme.gridEnabled = false;
                    text = "Show\nGrid";
                } else {
                    surfacePlot.theme.gridEnabled = true;
                    text = "Hide\nGrid";
                }
            }
        }
    }

    function checkState() {
        if (heightSeries.drawMode & Surface3DSeries.DrawSurface)
            surfaceToggle.text = "Hide\nSurface";
        else
            surfaceToggle.text = "Show\nSurface";

        if (heightSeries.drawMode & Surface3DSeries.DrawWireframe)
            surfaceGridToggle.text = "Hide Surface\nGrid";
        else
            surfaceGridToggle.text = "Show Surface\nGrid";
    }
}
