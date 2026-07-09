// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
// Qt-Security score:significant reason:default

#ifndef TESTIMPLICITCONVERSIONS_H
#define TESTIMPLICITCONVERSIONS_H

#include <QtCore/qobject.h>

class AbstractMetaBuilder;

class TestImplicitConversions : public QObject
{
    Q_OBJECT
private slots:
    void testWithPrivateCtors();
    void testWithModifiedVisibility();
    void testWithAddedCtor();
    void testWithExternalConversionOperator();
};

#endif
