// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TESTCTORINFORMATION_H
#define TESTCTORINFORMATION_H

#include <QtCore/QObject>

class AbstractMetaBuilder;

class TestCtorInformation: public QObject
{
    Q_OBJECT
private slots:
    void testCtorIsPrivate();
    void testHasNonPrivateCtor();
};

#endif // TESTCTORINFORMATION_H
