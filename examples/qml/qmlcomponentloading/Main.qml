// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    width: 400
    height: 220
    visible: true
    title: qsTr("QML Component Loading")

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 16

        Label {
            text: "A QML Person is created and driven from Python."
            Layout.alignment: Qt.AlignHCenter
        }
        Label {
            text: "See the terminal for the composition output."
            Layout.alignment: Qt.AlignHCenter
        }
    }
}
