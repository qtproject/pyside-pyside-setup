// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

pragma ComponentBehavior: Bound

import QtQuick

import ColorPalette

Window {
    id: window
    width: 500
    height: 400
    visible: true
    title: qsTr("Color Palette Client")

    enum DataView {
        UserView = 0,
        ColorView = 1
    }

    ServerSelection {
        id: serverview
        anchors.fill: parent
        onServerSelected: {colorview.visible = true; serverview.visible = false}
        colorResources: colors
        restPalette: paletteService
        colorUsers: users
    }

    ColorView {
        id: colorview
        anchors.fill: parent
        visible: false
        loginService: colorLogin
        colors: colors
        colorViewUsers: users
    }

    //! [RestService QML element]
    RestService {
        id: paletteService

        PaginatedColorUsersResource {
            id: users
            path: "/api/users"
        }

        PaginatedColorsResource {
            id: colors
            path: "/api/unknown"
        }

        BasicLogin {
            id: colorLogin
            loginPath: "/api/login"
            logoutPath: "/api/logout"
        }
    }
    //! [RestService QML element]

}
