// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TESTREVERSEOPERATORS_H
#define TESTREVERSEOPERATORS_H
#include <QtCore/QObject>

class TestReverseOperators : public QObject
{
    Q_OBJECT
private slots:
    void testReverseSum();
    void testReverseSumWithAmbiguity();
    void testSpaceshipOperator();
};

#endif
