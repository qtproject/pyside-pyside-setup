// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick.Controls
import QtLocation
import QtPositioning
import MapViewer

ApplicationWindow {
    id: appWindow
    property variant mapview
    property variant minimap
    property variant plugin
    property variant parameters

    //defaults
    //! [routecoordinate]
    property variant fromCoordinate: QtPositioning.coordinate(59.9483, 10.7695)
    property variant toCoordinate: QtPositioning.coordinate(59.9645, 10.671)
    //! [routecoordinate]

    function createMap(provider)
    {
        if (parameters && parameters.length>0)
            plugin = Qt.createQmlObject ('import QtLocation; Plugin{ name:"' + provider + '"; parameters: appWindow.parameters}', appWindow)
        else
            plugin = Qt.createQmlObject ('import QtLocation; Plugin{ name:"' + provider + '"}', appWindow)

        if (minimap) {
            minimap.destroy()
            minimap = null
        }

        var zoomLevel = null
        var tilt = null
        var bearing = null
        var fov = null
        var center = null
        var panelExpanded = null
        if (mapview) {
            zoomLevel = mapview.zoomLevel
            tilt = mapview.tilt
            bearing = mapview.bearing
            fov = mapview.fieldOfView
            center = mapview.center
            panelExpanded = mapview.slidersExpanded
            mapview.destroy()
        }
        mapview = mapComponent.createObject(page);
        mapview.map.plugin = plugin;

        if (zoomLevel != null) {
            mapview.map.tilt = tilt
            mapview.map.bearing = bearing
            mapview.map.fieldOfView = fov
            mapview.map.zoomLevel = zoomLevel
            mapview.map.center = center
            mapview.map.slidersExpanded = panelExpanded
        } else {
            // Use an integer ZL to enable nearest interpolation, if possible.
            mapview.map.zoomLevel = Math.floor((mapview.map.maximumZoomLevel - mapview.map.minimumZoomLevel)/2)
            // defaulting to 45 degrees, if possible.
            mapview.map.fieldOfView = Math.min(Math.max(45.0, mapview.map.minimumFieldOfView), mapview.maximumFieldOfView)
        }

        mapview.forceActiveFocus()
    }

    function getPlugins()
    {
        var plugin = Qt.createQmlObject ('import QtLocation; Plugin {}', appWindow)
        var myArray = new Array()
        for (var i = 0; i<plugin.availableServiceProviders.length; i++) {
            var tempPlugin = Qt.createQmlObject ('import QtLocation; Plugin {name: "' + plugin.availableServiceProviders[i]+ '"}', appWindow)
            if (tempPlugin.supportsMapping())
                myArray.push(tempPlugin.name)
        }
        myArray.sort()
        return myArray
    }

    function initializeProviders(pluginParameters)
    {
        var parameters = new Array()
        for (var prop in pluginParameters){
            var parameter = Qt.createQmlObject('import QtLocation; PluginParameter{ name: "'+ prop + '"; value: "' + pluginParameters[prop]+'"}',appWindow)
            parameters.push(parameter)
        }
        appWindow.parameters = parameters
        var plugins = getPlugins()
        mainMenu.providerMenu.createMenu(plugins)
        for (var i = 0; i<plugins.length; i++) {
            if (plugins[i] === "osm")
                mainMenu.selectProvider(plugins[i])
        }
    }

    title: qsTr("Mapviewer")
    height: 640
    width: 360
    visible: true
    menuBar: mainMenu

    //! [geocode0]
    Address {
        id :fromAddress
        street: "Sandakerveien 116"
        city: "Oslo"
        country: "Norway"
        state : ""
        postalCode: "0484"
    }
    //! [geocode0]

    Address {
        id: toAddress
        street: "Holmenkollveien 140"
        city: "Oslo"
        country: "Norway"
        postalCode: "0791"
    }

    MainMenu {
        id: mainMenu
        plugin: appWindow.plugin

        function toggleMiniMapState()
        {
            console.log("MiniMap with " + plugin)
            if (minimap) {
                minimap.destroy()
                minimap = null
            } else {
                minimap = Qt.createQmlObject ('import "map"; MiniMap{ z: mapview.z + 2 }', mapview)
            }
        }

        function setLanguage(lang)
        {
            mapview.map.plugin.locales = lang;
            stackView.pop(page)
        }

        onSelectProvider: (providerName) => {
            stackView.pop()
            for (var i = 0; i < providerMenu.count; i++) {
                providerMenu.actionAt(i).checked = providerMenu.actionAt(i).text === providerName
            }

            createMap(providerName)
            if (mapview.error === mapview.NoError) {
                selectMapType(mapview.map.activeMapType)
            } else {
                mainMenu.clearMenu(mapTypeMenu)
            }
        }

        onSelectMapType: (mapType) => {
            stackView.pop(page)
            for (var i = 0; i < mapTypeMenu.count; i++) {
                mapTypeMenu.actionAt(i).checked = mapTypeMenu.actionAt(i).text === mapType.name
            }
            mapview.map.activeMapType = mapType
        }


        onSelectTool: (tool) => {
            switch (tool) {
            case "AddressRoute":
                stackView.pop({item:page, immediate: true})
                stackView.push("forms/RouteAddress.qml" ,
                                   { "plugin": mapview.map.plugin,
                                       "toAddress": toAddress,
                                       "fromAddress": fromAddress})
                stackView.currentItem.showRoute.connect(mapview.calculateCoordinateRoute)
                stackView.currentItem.showMessage.connect(stackView.showMessage)
                stackView.currentItem.closeForm.connect(stackView.closeForm)
                break
            case "CoordinateRoute":
                stackView.pop({item:page, immediate: true})
                stackView.push("forms/RouteCoordinate.qml" ,
                                    { "toCoordinate": toCoordinate,
                                       "fromCoordinate": fromCoordinate})
                stackView.currentItem.showRoute.connect(mapview.calculateCoordinateRoute)
                stackView.currentItem.closeForm.connect(stackView.closeForm)
                break
            case "Geocode":
                stackView.pop({item:page, immediate: true})
                stackView.push("forms/Geocode.qml",
                                   { "address": fromAddress})
                stackView.currentItem.showPlace.connect(mapview.geocode)
                stackView.currentItem.closeForm.connect(stackView.closeForm)
                break
            case "RevGeocode":
                stackView.pop({item:page, immediate: true})
                stackView.push("forms/ReverseGeocode.qml",
                                    { "coordinate": fromCoordinate })
                stackView.currentItem.showPlace.connect(mapview.geocode)
                stackView.currentItem.closeForm.connect(stackView.closeForm)
                break
            case "Language":
                stackView.pop({item:page, immediate: true})
                stackView.push("forms/Locale.qml",
                                   { "locale":  mapview.map.plugin.locales[0]})
                stackView.currentItem.selectLanguage.connect(setLanguage)
                stackView.currentItem.closeForm.connect(stackView.closeForm)
                break
            case "Clear":
                mapview.map.clearData()
                break
            case "Prefetch":
                mapview.map.prefetchData()
                break
            default:
                console.log("Unsupported operation")
            }
        }

        onToggleMapState: (state) => {
            stackView.pop(page)
            switch (state) {
            case "FollowMe":
                mapview.followme = !mapview.followme
                break
            case "MiniMap":
                toggleMiniMapState()
                isMiniMap = minimap
                break
            default:
                console.log("Unsupported operation")
            }
        }
    }

    MapPopupMenu {
        id: mapPopupMenu

        function show(coordinate)
        {
            stackView.pop(page)
            mapPopupMenu.coordinate = coordinate
            mapPopupMenu.markersCount = mapview.markers.length
            mapPopupMenu.mapItemsCount = mapview.mapItems.length
            mapPopupMenu.popup()
        }

        onItemClicked: (item) => {
            stackView.pop(page)
            switch (item) {
            case "addMarker":
                mapview.addMarker()
                break
            case "getCoordinate":
                mapview.coordinatesCaptured(coordinate.latitude, coordinate.longitude)
                break
            case "fitViewport":
                mapview.map.fitViewportToMapItems()
                break
            case "deleteMarkers":
                mapview.deleteMarkers()
                break
            default:
                console.log("Unsupported operation:", item)
            }
        }
    }

    MarkerPopupMenu {
        id: markerPopupMenu

        function show(coordinate)
        {
            stackView.pop(page)
            markerPopupMenu.markersCount = mapview.markers.length
            markerPopupMenu.currentMarker = mapview.currentMarker
            markerPopupMenu.popup()
        }

        function askForCoordinate()
        {
            stackView.push("forms/ReverseGeocode.qml",
                                { "title": qsTr("New Coordinate"),
                                   "coordinate":   mapview.markers[mapview.currentMarker].coordinate})
            stackView.currentItem.showPlace.connect(moveMarker)
            stackView.currentItem.closeForm.connect(stackView.closeForm)
        }

        function moveMarker(coordinate)
        {
            mapview.markers[mapview.currentMarker].coordinate = coordinate;
            mapview.map.center = coordinate;
            stackView.pop(page)
        }

        onItemClicked: (item) => {
            stackView.pop(page)
            switch (item) {
            case "deleteMarker":
                mapview.deleteMarker(mapview.currentMarker)
                break;
            case "getMarkerCoordinate":
                mapview.coordinatesCaptured(mapview.markers[mapview.currentMarker].coordinate.latitude,
                                            mapview.markers[mapview.currentMarker].coordinate.longitude)
                break;
            case "moveMarkerTo":
                askForCoordinate()
                break;
            case "routeToNextPoint":
            case "routeToNextPoints":
                mapview.calculateMarkerRoute()
                break
            case "distanceToNextPoint":
                var coordinate1 = mapview.markers[mapview.currentMarker].coordinate;
                var coordinate2 = mapview.markers[mapview.currentMarker+1].coordinate;
                var distance = Helper.formatDistance(coordinate1.distanceTo(coordinate2));
                stackView.showMessage(qsTr("Distance"),"<b>" + qsTr("Distance:") + "</b> " + distance)
                break
            default:
                console.log("Unsupported operation:", item)
            }
        }
    }

    ItemPopupMenu {
        id: itemPopupMenu

        function show(type,coordinate)
        {
            stackView.pop(page)
            itemPopupMenu.type = type
            itemPopupMenu.popup()
        }

        onItemClicked: {
            stackView.pop(page)
            switch (item) {
            case "showRouteInfo":
                stackView.showRouteListPage()
                break;
            case "deleteRoute":
                mapview.routeModel.reset();
                break;
            case "showPointInfo":
                mapview.showGeocodeInfo()
                break;
            case "deletePoint":
                geocodeModel.reset()
                break;
            default:
                console.log("Unsupported operation")
            }
        }
    }

    StackView {
        id: stackView
        anchors.fill: parent
        focus: true
        initialItem: Item {
            id: page

            Text {
                visible: !supportsSsl && map && mapview.activeMapType && activeMapType.metadata.isHTTPS
                text: "The active map type\n
requires (missing) SSL\n
support"
                horizontalAlignment: Text.AlignHCenter
                font.pixelSize: appWindow.width / 12
                font.bold: true
                color: "grey"
                anchors.centerIn: parent
                z: 12
            }
        }

        function showMessage(title,message,backPage)
        {
            push("forms/Message.qml",
                               {
                                   "title" : title,
                                   "message" : message,
                                   "backPage" : backPage
                               })
            currentItem.closeForm.connect(closeMessage)
        }

        function closeMessage(backPage)
        {
            pop(backPage)
        }

        function closeForm()
        {
            pop(page)
        }

        function showRouteListPage()
        {
            push("forms/RouteList.qml",
                               {
                                   "routeModel" : mapview.routeModel
                               })
            currentItem.closeForm.connect(closeForm)
        }
    }

    Component {
        id: mapComponent

        MapComponent {
            width: page.width
            height: page.height
            onFollowmeChanged: mainMenu.isFollowMe = followme
            map.onSupportedMapTypesChanged: mainMenu.mapTypeMenu.createMenu(map)
            onCoordinatesCaptured: (latitude, longitude) => {
                var text = "<b>" + qsTr("Latitude:") + "</b> " + Helper.roundNumber(latitude,4) + "<br/><b>" + qsTr("Longitude:") + "</b> " + Helper.roundNumber(longitude,4)
                stackView.showMessage(qsTr("Coordinates"),text);
            }
            onGeocodeFinished:{
                if (geocodeModel.status == GeocodeModel.Ready) {
                    if (geocodeModel.count == 0) {
                        stackView.showMessage(qsTr("Geocode Error"),qsTr("Unsuccessful geocode"))
                    } else if (geocodeModel.count > 1) {
                        stackView.showMessage(qsTr("Ambiguous geocode"), geocodeModel.count + " " +
                                              qsTr("results found for the given address, please specify location"))
                    } else {
                        stackView.showMessage(qsTr("Location"), geocodeMessage(),page)
                    }
                } else if (geocodeModel.status == GeocodeModel.Error) {
                    stackView.showMessage(qsTr("Geocode Error"),qsTr("Unsuccessful geocode"))
                }
            }
            onRouteError: stackView.showMessage(qsTr("Route Error"),qsTr("Unable to find a route for the given points"),page)

            onShowGeocodeInfo: stackView.showMessage(qsTr("Location"),geocodeMessage(),page)

            map.onErrorChanged: {
                if (map.error != mapview.NoError) {
                    var title = qsTr("ProviderError")
                    var message =  mapview.errorString + "<br/><br/><b>" + qsTr("Try to select other provider") + "</b>"
                    if (map.error == mapview.MissingRequiredParameterError)
                        message += "<br/>" + qsTr("or see") + " \'mapviewer --help\' "
                                + qsTr("how to pass plugin parameters.")
                    stackView.showMessage(title,message);
                }
            }
            onShowMainMenu: (coordinate) => mapPopupMenu.show(coordinate)
            onShowMarkerMenu: (coordinate) => markerPopupMenu.show(coordinate)
            onShowRouteMenu: (coordinate) => itemPopupMenu.show("Route",coordinate)
            onShowPointMenu: (coordinate) => itemPopupMenu.show("Point",coordinate)
            onShowRouteList: stackView.showRouteListPage()

            TapHandler {
                onTapped: {
                }
            }
        }
    }
}
