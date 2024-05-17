// Copyright (C) 2024 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick.Layouts
import QtGraphs

Item {
    id: mainView
    width: 1280
    height: 720

    RowLayout  {
        id: graphsRow

        readonly property real margin:  mainView.width * 0.02

        anchors.fill: parent
        anchors.margins: margin
        spacing: margin

        Rectangle {
            Layout.fillHeight: true
            Layout.fillWidth: true
            color: "#262626"
            border.color: "#4d4d4d"
            border.width: 1
            radius: graphsRow.margin
            //! [bargraph]
            GraphsView {
                anchors.fill: parent
                anchors.margins: 16
                axisX: BarCategoryAxis {
                    categories: [2024, 2025, 2026]
                    gridVisible: false
                    subGridVisible: false
                }
                axisY: ValueAxis {
                    min: 20
                    max: 100
                    tickInterval: 10
                    subTickCount: 9
                }
                theme: GraphsTheme {
                    colorScheme: Qt.Dark
                    theme: GraphsTheme.Theme.QtGreen
                }
                //! [bargraph]
                //! [barseries]
                BarSeries {
                    //! [barseries]
                    //! [barset]
                    BarSet {
                        values: [82, 50, 75]
                        borderWidth: 2
                        color: "#373F26"
                        borderColor: "#DBEB00"
                    }
                    //! [barset]
                }
            }
        }

        Rectangle {
            Layout.fillHeight: true
            Layout.fillWidth: true
            color: "#262626"
            border.color: "#4d4d4d"
            border.width: 1
            radius: graphsRow.margin

            //! [linegraph]
            GraphsView {
                anchors.fill: parent
                anchors.margins: 16
                theme: GraphsTheme {
                    readonly property color c1: "#DBEB00"
                    readonly property color c2: "#373F26"
                    readonly property color c3: Qt.lighter(c2, 1.5)
                    colorScheme: Qt.Dark
                    seriesColors: ["#2CDE85", "#DBEB00"]
                    grid.mainColor: c3
                    grid.subColor: c2
                    axisX.mainColor: c3
                    axisY.mainColor: c3
                    axisX.subColor: c2
                    axisY.subColor: c2
                    axisX.labelTextColor: c1
                    axisY.labelTextColor: c1
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
                //! [linegraph]

                //! [linemarker]
                component Marker : Rectangle {
                    width: 16
                    height: 16
                    color: "#ffffff"
                    radius: width * 0.5
                    border.width: 4
                    border.color: "#000000"
                }
                //! [linemarker]

                //! [lineseries1]
                LineSeries {
                    id: lineSeries1
                    width: 4
                    pointDelegate: Marker { }
                    XYPoint { x: 0; y: 0 }
                    XYPoint { x: 1; y: 2.1 }
                    XYPoint { x: 2; y: 3.3 }
                    XYPoint { x: 3; y: 2.1 }
                    XYPoint { x: 4; y: 4.9 }
                    XYPoint { x: 5; y: 3.0 }
                }
                //! [lineseries1]

                //! [lineseries2]
                LineSeries {
                    id: lineSeries2
                    width: 4
                    pointDelegate: Marker { }
                    XYPoint { x: 0; y: 5.0 }
                    XYPoint { x: 1; y: 3.3 }
                    XYPoint { x: 2; y: 7.1 }
                    XYPoint { x: 3; y: 7.5 }
                    XYPoint { x: 4; y: 6.1 }
                    XYPoint { x: 5; y: 3.2 }
                }
                //! [lineseries2]
            }
        }
    }
}
