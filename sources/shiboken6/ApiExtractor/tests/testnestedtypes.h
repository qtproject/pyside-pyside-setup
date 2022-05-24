// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TESTNESTEDTYPES_H
#define TESTNESTEDTYPES_H

#include <QtCore/QObject>

class TestNestedTypes : public QObject
{
    Q_OBJECT
private slots:
    void testNestedTypesModifications();
    void testDuplicationOfNestedTypes();
};

#endif
