// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Dialogs

Window {
    id: window
    width: 500
    height: 400
    minimumWidth: 500
    minimumHeight: 400
    visible: true
    title: qsTr("Color Palette Client")

    enum DataView {
        UserView = 0,
        ColorView = 1
    }

    // The Qt colorpalette REST API server listens here, so the client
    // just connects on startup.
    required property var serverUrl

    ColorView {
        id: colorview
        anchors.fill: parent
        loginService: colorLogin
        colors: colorPalette
        colorViewUsers: users
    }

    MessageDialog {
        id: connectionErrorDialog
        title: qsTr("Connection failed")
        text: qsTr("Could not reach the server at %1.").arg(window.serverUrl)
        informativeText: qsTr("Start the Qt colorpalette REST API server "
            + "on port 49425, then retry.")
        buttons: MessageDialog.Cancel | MessageDialog.Retry
        onButtonClicked: function(button) {
            if (button === MessageDialog.Retry) {
                colorPalette.refreshCurrentPage()
                users.refreshCurrentPage()
            } else if (button === MessageDialog.Cancel) {
                Qt.quit()
            }
        }
    }

    Connections {
        target: colorPalette
        function onErrorOccurred(message) { connectionErrorDialog.open() }
    }

    //! [RestService QML element]
    RestService {
        id: paletteService
        url: window.serverUrl

        PaginatedResource {
            id: users
            path: "users"
        }

        PaginatedResource {
            id: colorPalette
            path: "unknown"
        }

        BasicLogin {
            id: colorLogin
            loginPath: "login"
            logoutPath: "logout"
        }
    }
    //! [RestService QML element]

    Component.onCompleted: {
        colorPalette.refreshCurrentPage()
        users.refreshCurrentPage()
    }
}
