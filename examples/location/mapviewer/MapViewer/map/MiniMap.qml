// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtPositioning
import QtLocation

Rectangle{

    function clamp(num, min, max)
    {
      return num < min ? min : num > max ? max : num;
    }

    function minimumScaleFactor()
    {
        var hscalefactor = (400.0 / Math.max(Math.min(mapview.width, 1000), 400)) * 0.5
        var vscalefactor = (400.0 / Math.max(Math.min(mapview.height, 1000), 400)) * 0.5
        return Math.min(hscalefactor,vscalefactor)
    }

    function avgScaleFactor()
    {
        var hscalefactor = (400.0 / Math.max(Math.min(mapview.width, 1000), 400)) * 0.5
        var vscalefactor = (400.0 / Math.max(Math.min(mapview.height, 1000), 400)) * 0.5
        return (hscalefactor+vscalefactor) * 0.5
    }

    id: miniMapRect
    width: Math.floor(mapview.width * avgScaleFactor()) + 2
    height: Math.floor(mapview.height * avgScaleFactor()) + 2
    anchors.right: (parent) ? parent.right : undefined
    anchors.rightMargin: 10
    anchors.top: (parent) ? parent.top : undefined
    anchors.topMargin: 10
    color: "#242424"
    Map {
        id: miniMap
        anchors.top: parent.top
        anchors.topMargin: 1
        anchors.left: parent.left
        anchors.leftMargin: 1
        width: Math.floor(mapview.width * avgScaleFactor())
        height: Math.floor(mapview.height * avgScaleFactor())
        zoomLevel: clamp(mapview.map.zoomLevel - 4.5, 1.0, 5.0) //(map.zoomLevel > minimumZoomLevel + 3) ? minimumZoomLevel + 3 : 1.5
        center: mapview.map.center
        plugin: mapview.map.plugin
        copyrightsVisible: false
        property double mapZoomLevel : mapview.map.zoomLevel

        // cannot use property bindings on map.visibleRegion in MapRectangle because it's non-NOTIFYable
        onCenterChanged: miniMapRectangle.updateCoordinates()
        onMapZoomLevelChanged: miniMapRectangle.updateCoordinates()
        onWidthChanged: miniMapRectangle.updateCoordinates()
        onHeightChanged: miniMapRectangle.updateCoordinates()

        MapRectangle {
            id: miniMapRectangle
            color: "#44ff0000"
            border.width: 1
            border.color: "red"
            autoFadeIn: false

            function getMapVisibleRegion()
            {
                return mapview.map.visibleRegion.boundingGeoRectangle()
            }

            function updateCoordinates()
            {
                topLeft.latitude =  getMapVisibleRegion().topLeft.latitude
                topLeft.longitude=  getMapVisibleRegion().topLeft.longitude
                bottomRight.latitude =  getMapVisibleRegion().bottomRight.latitude
                bottomRight.longitude=  getMapVisibleRegion().bottomRight.longitude
            }
        }
    }
}
