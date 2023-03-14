// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: mainView
    width: 1280
    height: 1024
    visible: true

    property bool portraitMode: width < height

    TabBar {
        id: tabBar
        width: parent.width

        TabButton {
            text: "Height Map"
        }

        TabButton {
            text: "Spectrogram"
        }

        TabButton {
            text: "Oscilloscope"
        }
    }

    StackLayout {
        anchors.top: tabBar.bottom
        anchors.bottom: parent.bottom
        width: parent.width
        currentIndex: tabBar.currentIndex

        SurfaceHeightMap {
            Layout.fillHeight: true
            Layout.fillWidth: true
            portraitMode: mainView.portraitMode
        }

        SurfaceSpectrogram {
            Layout.fillHeight: true
            Layout.fillWidth: true
            portraitMode: mainView.portraitMode
        }

        SurfaceOscilloscope {
            Layout.fillHeight: true
            Layout.fillWidth: true
            portraitMode: mainView.portraitMode
        }
    }
}
