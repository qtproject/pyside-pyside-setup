// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtGraphs

Rectangle {
    id: graphContainer
    width: 1280
    height: 720
    property alias theme: lines.theme

    color: "white"

    GraphsView {
        id: lines
        anchors.fill: parent
        anchors.margins: 16
        theme: GraphsTheme {
            grid.mainColor: "darkgrey"
            grid.subColor: "lightgrey"
            labelTextColor: "black"
            plotAreaBackgroundColor: "white"
            backgroundColor: "white"
            colorScheme: Qt.Light
        }
        axisX: ValueAxis {
            max: 5
            tickInterval: 1
            subTickCount: 9
            labelDecimals: 1
        }
        axisY: ValueAxis {
            max: 10
            tickInterval: 1
            subTickCount: 4
            labelDecimals: 1
        }

        component Marker : Rectangle {
            width: 8
            height: 8
            color: "#ffffff"
            radius: width * 0.5
            border.width: 4
            border.color: "#000000"
        }

        LineSeries {
            id: lineSeries1
            width: 4
            pointDelegate: Marker { }
            color: "black"
            XYPoint { x: 0; y: 0 }
            XYPoint { x: 1; y: 2.1 }
            XYPoint { x: 2; y: 3.3 }
            XYPoint { x: 3; y: 2.1 }
            XYPoint { x: 4; y: 4.9 }
            XYPoint { x: 5; y: 3.0 }
        }

        LineSeries {
            id: lineSeries2
            width: 4
            pointDelegate: Marker { }
            color: "black"
            XYPoint { x: 0; y: 5.0 }
            XYPoint { x: 1; y: 3.3 }
            XYPoint { x: 2; y: 7.1 }
            XYPoint { x: 3; y: 7.5 }
            XYPoint { x: 4; y: 6.1 }
            XYPoint { x: 5; y: 3.2 }
        }
    }
}
