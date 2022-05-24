// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TESTABSTRACTMETATYPE_H
#define TESTABSTRACTMETATYPE_H

#include <QtCore/QObject>

class TestAbstractMetaType : public QObject
{
    Q_OBJECT
private slots:
    void parsing_data();
    void parsing();
    void testConstCharPtrType();
    void testCharType();
    void testTypedef();
    void testTypedefWithTemplates();
    void testApiVersionSupported();
    void testApiVersionNotSupported();
    void testObjectTypeUsedAsValue();
};

#endif
