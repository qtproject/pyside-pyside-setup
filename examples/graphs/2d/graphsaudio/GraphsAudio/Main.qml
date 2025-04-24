// Copyright (C) 2025 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick.Controls
import QtGraphs

ApplicationWindow {
    visible: true
    width: 1000
    height: 800
    title: "Data from the microphone (" + device_name + ")"

    GraphsView {
        id: graph
        anchors.fill: parent

        LineSeries {
            id: audio_series
            width: 2
            color: "#007acc"
        }

        axisX: ValueAxis  {
            min: 0
            max: 2000
            tickInterval : 500
            labelFormat: "%g"
            titleText: "Samples"
        }

        axisY: ValueAxis  {
            min: -1
            max: 1
            tickInterval : 0.5
            labelFormat: "%0.1f"
            titleText: "Audio level"
        }
    }

    Connections {
        target: audio_bridge
        function onDataUpdated(buffer) {
            audio_series.clear()
            for (let i = 0; i < buffer.length; ++i) {
                audio_series.append(buffer[i])
            }
        }
    }
}
