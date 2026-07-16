// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick
import QtQuick.Controls

ApplicationWindow {
    width: 420
    height: 260
    visible: true
    title: qsTr("Qt Controls from Python")

    // Python will create QtQuick Controls widgets and parent them here.
    // The window intentionally has no children defined in QML. Everything
    // is instantiated and wired up from Python via load_qml_component.
}
