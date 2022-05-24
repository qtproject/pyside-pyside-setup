// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TESTCONTAINER_H
#define TESTCONTAINER_H
#include <QtCore/QObject>

class TestContainer : public QObject
{
    Q_OBJECT
private slots:
    void testContainerType();
    void testListOfValueType();
};

#endif
