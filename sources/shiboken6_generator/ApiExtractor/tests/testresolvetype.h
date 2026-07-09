// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
// Qt-Security score:significant reason:default

#ifndef TESTRESOLVETYPE_H
#define TESTRESOLVETYPE_H

#include <QtCore/qobject.h>

class TestResolveType : public QObject
{
    Q_OBJECT
    private slots:
        void initTestCase();

        void testResolveReturnTypeFromParentScope();
        void testFixDefaultArguments_data();
        void testFixDefaultArguments();
        void testCppTypes();
};

#endif
