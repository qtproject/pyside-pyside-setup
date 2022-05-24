// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import QtQuick 2.0
import test.ListModel 1.0

ListView {
    required property ListModel pythonModel
    width: 300; height: 300
    delegate: Text { text: pysideModelData }
    model: pythonModel
}

