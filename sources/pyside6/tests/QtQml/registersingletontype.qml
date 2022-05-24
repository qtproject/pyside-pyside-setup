// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import QtQuick 2.0
import Singletons 1.0

Item {
    Component.onCompleted: {
        SingletonQObjectCallback.data += SingletonQObjectNoCallback.data
            + SingletonQJSValue.data
            + SingletonInstance.data
            + DecoratedSingletonQObject.data;
    }
}
