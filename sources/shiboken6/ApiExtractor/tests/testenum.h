// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TESTENUM_H
#define TESTENUM_H

#include <QtCore/QObject>

class TestEnum : public QObject
{
    Q_OBJECT
private slots:
    void testEnumCppSignature();
    void testEnumWithApiVersion();
    void testAnonymousEnum();
    void testGlobalEnums();
    void testEnumValueFromNeighbourEnum();
    void testEnumValueFromExpression();
    void testPrivateEnum();
    void testTypedefEnum();
    void testEnumDefaultValues_data();
    void testEnumDefaultValues();
};

#endif
