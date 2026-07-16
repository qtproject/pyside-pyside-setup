// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import QtQuick

QtObject {
    property string name: "John"
    property int age: 30
    signal birthdayHappened()
    function celebrateBirthday() {
        age++
        birthdayHappened()
    }
}
