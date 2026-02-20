// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtGraphs

Item {
    id: graphContainer
    width: 1280
    height: 720
    property alias theme: bars.theme

    Bars3D {
        id: bars
        anchors.fill: parent
        msaaSamples: 8
        cameraPreset: Graphs3D.CameraPreset.IsometricLeftHigh

        theme: GraphsTheme {
            backgroundColor: "white"
            plotAreaBackgroundVisible: false
            grid.mainColor: "black"
            labelFont.pointSize: 20
            labelBackgroundVisible: false
            colorScheme: Qt.Light
        }

        Bar3DSeries {
            id: series
            itemLabelFormat: "Expenses, @colLabel, @rowLabel: -@valueLabel"
            baseGradient: gradient
            colorStyle: GraphsTheme.ColorStyle.RangeGradient

            ItemModelBarDataProxy {
                id: barProxy
                itemModel: ListModel {
                    ListElement{ coords: "0,0"; data: "4.75"; }
                    ListElement{ coords: "1,0"; data: "3.00"; }
                    ListElement{ coords: "0,1"; data: "3.55"; }
                    ListElement{ coords: "1,1"; data: "3.03"; }
                    ListElement{ coords: "0,2"; data: "3.37"; }
                    ListElement{ coords: "1,2"; data: "2.98"; }
                    ListElement{ coords: "0,3"; data: "5.34"; }
                    ListElement{ coords: "1,3"; data: "4.54"; }
                    ListElement{ coords: "0,4"; data: "6.01"; }
                    ListElement{ coords: "1,4"; data: "5.83"; }
                }
                rowRole: "coords"
                columnRole: "coords"
                valueRole: "data"
                rowRolePattern: /(\d),(\d)/
                columnRolePattern: /(\d),(\d)/
                rowRoleReplace: "\\1"
                columnRoleReplace: "\\2"
            }

            Gradient {
                id: gradient
                GradientStop { position: 1.0; color: "#5000FF" }
                GradientStop { position: 0.0; color: "#2000FF" }
            }
        }
    }
}
