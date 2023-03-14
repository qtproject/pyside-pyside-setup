// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick.Controls
import QtDataVisualization
//! [0]
import SurfaceGallery
//! [0]

Item {
    id: oscilloscopeView

    property int sampleColumns: sampleSlider.value
    property int sampleRows: sampleColumns / 2
    property int sampleCache: 24

    required property bool portraitMode

    property real controlWidth: oscilloscopeView.portraitMode ? oscilloscopeView.width - 10
                                                              : oscilloscopeView.width / 4 - 6.66

    property real buttonWidth: oscilloscopeView.portraitMode ? oscilloscopeView.width - 10
                                                             : oscilloscopeView.width / 3 - 7.5

    onSampleRowsChanged: {
        surfaceSeries.selectedPoint = surfaceSeries.invalidSelectionPosition
        generateData()
    }

    //![1]
    DataSource {
        id: dataSource
    }
    //![1]

    Item {
        id: dataView
        anchors.bottom: parent.bottom
        width: parent.width
        height: parent.height - controlArea.height

        //! [2]
        Surface3D {
            id: surfaceGraph
            anchors.fill: parent

            Surface3DSeries {
                id: surfaceSeries
                drawMode: Surface3DSeries.DrawSurfaceAndWireframe
                itemLabelFormat: "@xLabel, @zLabel: @yLabel"
                //! [2]
                //! [3]
                itemLabelVisible: false
                //! [3]

                //! [4]
                onItemLabelChanged: {
                    if (surfaceSeries.selectedPoint == surfaceSeries.invalidSelectionPosition)
                        selectionText.text = "No selection";
                    else
                        selectionText.text = surfaceSeries.itemLabel;
                }
                //! [4]
            }

            shadowQuality: AbstractGraph3D.ShadowQualityNone
            selectionMode: AbstractGraph3D.SelectionSlice | AbstractGraph3D.SelectionItemAndColumn
            theme: Theme3D {
                type: Theme3D.ThemeIsabelle
                backgroundEnabled: false
            }
            scene.activeCamera.cameraPreset: Camera3D.CameraPresetFrontHigh

            axisX.labelFormat: "%d ms"
            axisY.labelFormat: "%d W"
            axisZ.labelFormat: "%d mV"
            axisX.min: 0
            axisY.min: 0
            axisZ.min: 0
            axisX.max: 1000
            axisY.max: 100
            axisZ.max: 800
            axisX.segmentCount: 4
            axisY.segmentCount: 4
            axisZ.segmentCount: 4
            measureFps: true
            renderingMode: AbstractGraph3D.RenderDirectToBackground

            onCurrentFpsChanged: (fps)=> {
                                     if (fps > 10)
                                     fpsText.text = "FPS: " + Math.round(surfaceGraph.currentFps);
                                     else
                                     fpsText.text = "FPS: " + Math.round(surfaceGraph.currentFps * 10.0) / 10.0;
                                 }

            //! [5]
            Component.onCompleted: oscilloscopeView.generateData();
            //! [5]
        }
    }

    //! [7]
    Timer {
        id: refreshTimer
        interval: 1000 / frequencySlider.value
        running: true
        repeat: true
        onTriggered: dataSource.update(surfaceSeries);
    }
    //! [7]

    Rectangle {
        id: controlArea
        height: oscilloscopeView.portraitMode ? flatShadingToggle.implicitHeight * 7
                                              : flatShadingToggle.implicitHeight * 2
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.right: parent.right
        color: surfaceGraph.theme.backgroundColor

        // Samples
        Rectangle {
            id: samples
            width: oscilloscopeView.controlWidth
            height: flatShadingToggle.implicitHeight
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.margins: 5

            color: surfaceGraph.theme.windowColor
            border.color: surfaceGraph.theme.gridLineColor
            border.width: 1
            radius: 4

            Row {
                anchors.centerIn: parent
                spacing: 10
                padding: 5

                Slider {
                    id: sampleSlider
                    from: oscilloscopeView.sampleCache * 2
                    to: from * 10
                    stepSize: oscilloscopeView.sampleCache

                    background: Rectangle {
                        x: sampleSlider.leftPadding
                        y: sampleSlider.topPadding + sampleSlider.availableHeight / 2
                           - height / 2
                        implicitWidth: 200
                        implicitHeight: 4
                        width: sampleSlider.availableWidth
                        height: implicitHeight
                        radius: 2
                        color: surfaceGraph.theme.gridLineColor

                        Rectangle {
                            width: sampleSlider.visualPosition * parent.width
                            height: parent.height
                            color: surfaceGraph.theme.labelTextColor
                            radius: 2
                        }
                    }

                    handle: Rectangle {
                        x: sampleSlider.leftPadding + sampleSlider.visualPosition
                           * (sampleSlider.availableWidth - width)
                        y: sampleSlider.topPadding + sampleSlider.availableHeight / 2
                           - height / 2
                        implicitWidth: 20
                        implicitHeight: 20
                        radius: 10
                        color: sampleSlider.pressed ? surfaceGraph.theme.gridLineColor
                                                    : surfaceGraph.theme.windowColor
                        border.color: sampleSlider.pressed ? surfaceGraph.theme.labelTextColor
                                                           : surfaceGraph.theme.gridLineColor
                    }

                    Component.onCompleted: value = from;
                }

                Text {
                    id: samplesText
                    text: "Samples: " + (oscilloscopeView.sampleRows * oscilloscopeView.sampleColumns)
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                    color: surfaceGraph.theme.labelTextColor
                }
            }
        }

        // Frequency
        Rectangle {
            id: frequency
            width: oscilloscopeView.controlWidth
            height: flatShadingToggle.implicitHeight
            anchors.left: oscilloscopeView.portraitMode ? parent.left : samples.right
            anchors.top: oscilloscopeView.portraitMode ? samples.bottom : parent.top
            anchors.margins: 5

            color: surfaceGraph.theme.windowColor
            border.color: surfaceGraph.theme.gridLineColor
            border.width: 1
            radius: 4

            Row {
                anchors.centerIn: parent
                spacing: 10
                padding: 5

                Slider {
                    id: frequencySlider
                    from: 2
                    to: 60
                    stepSize: 2
                    value: 30

                    background: Rectangle {
                        x: frequencySlider.leftPadding
                        y: frequencySlider.topPadding + frequencySlider.availableHeight / 2
                           - height / 2
                        implicitWidth: 200
                        implicitHeight: 4
                        width: frequencySlider.availableWidth
                        height: implicitHeight
                        radius: 2
                        color: surfaceGraph.theme.gridLineColor

                        Rectangle {
                            width: frequencySlider.visualPosition * parent.width
                            height: parent.height
                            color: surfaceGraph.theme.labelTextColor
                            radius: 2
                        }
                    }

                    handle: Rectangle {
                        x: frequencySlider.leftPadding + frequencySlider.visualPosition
                           * (frequencySlider.availableWidth - width)
                        y: frequencySlider.topPadding + frequencySlider.availableHeight / 2
                           - height / 2
                        implicitWidth: 20
                        implicitHeight: 20
                        radius: 10
                        color: frequencySlider.pressed ? surfaceGraph.theme.gridLineColor
                                                       : surfaceGraph.theme.windowColor
                        border.color: frequencySlider.pressed ? surfaceGraph.theme.labelTextColor
                                                              : surfaceGraph.theme.gridLineColor
                    }
                }

                Text {
                    id: frequencyText
                    text: "Freq: " + frequencySlider.value + " Hz"
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                    color: surfaceGraph.theme.labelTextColor
                }
            }
        }

        // FPS
        Rectangle {
            id: fpsindicator
            width: oscilloscopeView.controlWidth
            height: flatShadingToggle.implicitHeight
            anchors.left: oscilloscopeView.portraitMode ? parent.left : frequency.right
            anchors.top: oscilloscopeView.portraitMode ? frequency.bottom : parent.top
            anchors.margins: 5

            color: surfaceGraph.theme.windowColor
            border.color: surfaceGraph.theme.gridLineColor
            border.width: 1
            radius: 4

            Text {
                id: fpsText
                anchors.fill: parent
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
                color: surfaceGraph.theme.labelTextColor
            }
        }

        // Selection
        Rectangle {
            id: selection
            width: oscilloscopeView.controlWidth
            height: flatShadingToggle.implicitHeight
            anchors.left: oscilloscopeView.portraitMode ? parent.left : fpsindicator.right
            anchors.top: oscilloscopeView.portraitMode ? fpsindicator.bottom : parent.top
            anchors.margins: 5

            color: surfaceGraph.theme.windowColor
            border.color: surfaceGraph.theme.gridLineColor
            border.width: 1
            radius: 4

            Text {
                id: selectionText
                anchors.fill: parent
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
                text: "No selection"
                color: surfaceGraph.theme.labelTextColor
            }
        }

        // Flat shading
        Button {
            id: flatShadingToggle
            width: oscilloscopeView.buttonWidth
            anchors.left: parent.left
            anchors.top: selection.bottom
            anchors.margins: 5

            text: surfaceSeries.flatShadingSupported ? "Show\nSmooth" : "Flat\nnot supported"
            enabled: surfaceSeries.flatShadingSupported

            onClicked: {
                if (surfaceSeries.flatShadingEnabled) {
                    surfaceSeries.flatShadingEnabled = false;
                    text = "Show\nFlat"
                } else {
                    surfaceSeries.flatShadingEnabled = true;
                    text = "Show\nSmooth"
                }
            }

            contentItem: Text {
                text: flatShadingToggle.text
                opacity: flatShadingToggle.enabled ? 1.0 : 0.3
                color: surfaceGraph.theme.labelTextColor
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                elide: Text.ElideRight
            }

            background: Rectangle {
                opacity: flatShadingToggle.enabled ? 1 : 0.3
                color: flatShadingToggle.down ? surfaceGraph.theme.gridLineColor
                                              : surfaceGraph.theme.windowColor
                border.color: flatShadingToggle.down ? surfaceGraph.theme.labelTextColor
                                                     : surfaceGraph.theme.gridLineColor
                border.width: 1
                radius: 2
            }
        }

        // Surface grid
        Button {
            id: surfaceGridToggle
            width: oscilloscopeView.buttonWidth
            anchors.left: oscilloscopeView.portraitMode ? parent.left : flatShadingToggle.right
            anchors.top: oscilloscopeView.portraitMode ? flatShadingToggle.bottom : selection.bottom
            anchors.margins: 5

            text: "Hide\nSurface Grid"

            onClicked: {
                if (surfaceSeries.drawMode & Surface3DSeries.DrawWireframe) {
                    surfaceSeries.drawMode &= ~Surface3DSeries.DrawWireframe;
                    text = "Show\nSurface Grid";
                } else {
                    surfaceSeries.drawMode |= Surface3DSeries.DrawWireframe;
                    text = "Hid\nSurface Grid";
                }
            }

            contentItem: Text {
                text: surfaceGridToggle.text
                color: surfaceGraph.theme.labelTextColor
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                elide: Text.ElideRight
            }

            background: Rectangle {
                color: surfaceGridToggle.down ? surfaceGraph.theme.gridLineColor
                                              : surfaceGraph.theme.windowColor
                border.color: surfaceGridToggle.down ? surfaceGraph.theme.labelTextColor
                                                     : surfaceGraph.theme.gridLineColor
                border.width: 1
                radius: 2
            }
        }

        // Exit
        Button {
            id: exitButton
            width: oscilloscopeView.buttonWidth
            height: surfaceGridToggle.height
            anchors.left: oscilloscopeView.portraitMode ? parent.left : surfaceGridToggle.right
            anchors.top: oscilloscopeView.portraitMode ? surfaceGridToggle.bottom : selection.bottom
            anchors.margins: 5

            text: "Quit"

            onClicked: Qt.quit();

            contentItem: Text {
                text: exitButton.text
                color: surfaceGraph.theme.labelTextColor
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                elide: Text.ElideRight
            }

            background: Rectangle {
                color: exitButton.down ? surfaceGraph.theme.gridLineColor
                                       : surfaceGraph.theme.windowColor
                border.color: exitButton.down ? surfaceGraph.theme.labelTextColor
                                              : surfaceGraph.theme.gridLineColor
                border.width: 1
                radius: 2
            }
        }
    }

    //! [6]
    function generateData() {
        dataSource.generateData(oscilloscopeView.sampleCache, oscilloscopeView.sampleRows,
                                oscilloscopeView.sampleColumns,
                                surfaceGraph.axisX.min, surfaceGraph.axisX.max,
                                surfaceGraph.axisY.min, surfaceGraph.axisY.max,
                                surfaceGraph.axisZ.min, surfaceGraph.axisZ.max);
    }
    //! [6]
}
