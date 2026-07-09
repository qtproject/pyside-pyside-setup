// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
// Qt-Security score:significant reason:default

#ifndef TESTVOIDARG_H
#define TESTVOIDARG_H

#include <QtCore/qobject.h>

class TestVoidArg : public QObject
{
    Q_OBJECT
private slots:
    void testVoidParsedFunction();
    void testVoidPointerParsedFunction();
    void testVoidAddedFunction();
};

#endif
