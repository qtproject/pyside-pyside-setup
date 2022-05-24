// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TESTDTORINFORMATION_H
#define TESTDTORINFORMATION_H

#include <QtCore/QObject>

class AbstractMetaBuilder;

class TestDtorInformation: public QObject
{
    Q_OBJECT
private slots:
    void testDtorIsPrivate();
    void testDtorIsProtected();
    void testDtorIsVirtual();
    void testDtorFromBaseIsVirtual();
    void testClassWithVirtualDtorIsPolymorphic();
};

#endif // TESTDTORINFORMATION_H
