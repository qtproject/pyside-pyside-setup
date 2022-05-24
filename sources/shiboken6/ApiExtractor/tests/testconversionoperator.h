// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TESTCONVERSIONOPERATOR_H
#define TESTCONVERSIONOPERATOR_H
#include <QtCore/QObject>

class TestConversionOperator : public QObject
{
    Q_OBJECT
private slots:
    void testConversionOperator();
    void testConversionOperatorOfDiscardedClass();
    void testRemovedConversionOperator();
    void testConversionOperatorReturningReference();
    void testConversionOperatorReturningConstReference();
};

#endif
