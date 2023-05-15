// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick.Controls

Menu {
    property variant coordinate
    property int markersCount
    property int mapItemsCount
    signal itemClicked(string item)

    MenuItem {
        text: qsTr("Add Marker")
        onTriggered: itemClicked("addMarker")
    }
    MenuItem {
        text: qsTr("Get coordinate")
        onTriggered: itemClicked("getCoordinate")
    }
    MenuItem {
        text: qsTr("Fit Viewport To Markers")
        onTriggered: itemClicked("fitViewport")
    }
    MenuItem {
        text: qsTr("Delete all markers")
        enabled: markersCount > 0
        onTriggered: itemClicked("deleteMarkers")
    }
}
