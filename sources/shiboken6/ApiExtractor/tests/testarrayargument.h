// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TESTARRAYARGUMENT_H
#define TESTARRAYARGUMENT_H
#include <QtCore/QObject>

class TestArrayArgument : public QObject
{
    Q_OBJECT
private slots:
    void testArrayArgumentWithSizeDefinedByInteger();
    void testArraySignature();
    void testArrayArgumentWithSizeDefinedByEnumValue();
    void testArrayArgumentWithSizeDefinedByEnumValueFromGlobalEnum();
};

#endif
