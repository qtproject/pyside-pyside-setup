// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick.Controls
import QtLocation

MenuBar {
    id: menuBar
    property variant providerMenu: providerMenu
    property variant mapTypeMenu: mapTypeMenu
    property variant toolsMenu: toolsMenu
    property variant plugin
    property alias isFollowMe: toolsMenu.isFollowMe
    property alias isMiniMap: toolsMenu.isMiniMap

    signal selectProvider(string providerName)
    signal selectMapType(variant mapType)
    signal selectTool(string tool);
    signal toggleMapState(string state)

    function clearMenu(menu)
    {
        while (menu.count)
            menu.removeItem(menu.itemAt(0))
    }

    Menu {
        id: providerMenu
        title: qsTr("Provider")

        function createMenu(plugins)
        {
            clearMenu(providerMenu)
            for (var i = 0; i < plugins.length; i++) {
                createProviderMenuItem(plugins[i]);
            }
        }

        function createProviderMenuItem(provider)
        {
            var action = Qt.createQmlObject('import QtQuick.Controls; Action{ text: "' + provider + '"; checkable: true; onTriggered: function(){selectProvider("' + provider + '")} }', providerMenu)
            addAction(action)
        }
    }

    Menu {
        id: mapTypeMenu
        title: qsTr("MapType")

        Component {
            id: mapTypeMenuActionComponent
            Action {

            }
        }
        function createMenu(map)
        {
            clearMenu(mapTypeMenu)
            for (var i = 0; i<map.supportedMapTypes.length; i++) {
                createMapTypeMenuItem(map.supportedMapTypes[i], map.activeMapType === map.supportedMapTypes[i]);
            }
        }

        function createMapTypeMenuItem(mapType, checked)
        {
            var action = mapTypeMenuActionComponent.createObject(mapTypeMenu, { text: mapType.name, checkable: true, checked: checked })
            action.triggered.connect(function(){selectMapType(mapType)})
            addAction(action)
        }
    }

    Menu {
        id: toolsMenu
        property bool isFollowMe: false;
        property bool isMiniMap: false;
        property variant plugin: menuBar.plugin

        title: qsTr("Tools")

        Action {
            text: qsTr("Reverse geocode")
            enabled: plugin ? plugin.supportsGeocoding(Plugin.ReverseGeocodingFeature) : false
            onTriggered: selectTool("RevGeocode")
        }
        MenuItem {
            text: qsTr("Geocode")
            enabled: plugin ? plugin.supportsGeocoding() : false
            onTriggered: selectTool("Geocode")
        }
        MenuItem {
            text: qsTr("Route with coordinates")
            enabled: plugin ? plugin.supportsRouting() : false
            onTriggered: selectTool("CoordinateRoute")
        }
        MenuItem {
            text: qsTr("Route with address")
            enabled: plugin ? plugin.supportsRouting() : false
            onTriggered: selectTool("AddressRoute")
        }
        MenuItem {
            text: isMiniMap ? qsTr("Hide minimap") : qsTr("Minimap")
            onTriggered: toggleMapState("MiniMap")
        }
        MenuItem {
            text: isFollowMe ? qsTr("Stop following") : qsTr("Follow me")
            onTriggered: toggleMapState("FollowMe")
        }
        MenuItem {
            text: qsTr("Language")
            onTriggered: selectTool("Language")
        }
        MenuItem {
            text: qsTr("Prefetch Map Data")
            onTriggered: selectTool("Prefetch")
        }
        MenuItem {
            text: qsTr("Clear Map Data")
            onTriggered: selectTool("Clear")
        }
    }
}
