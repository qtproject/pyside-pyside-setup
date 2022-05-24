// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TESTABSTRACTMETACLASS_H
#define TESTABSTRACTMETACLASS_H

#include <QtCore/QObject>

class TestModifyFunction : public QObject
{
    Q_OBJECT
    private slots:
        void testOwnershipTransfer();
        void testWithApiVersion();
        void testAllowThread();
        void testRenameArgument_data();
        void testRenameArgument();
        void invalidateAfterUse();
        void testGlobalFunctionModification();
        void testScopedModifications_data();
        void testScopedModifications();
        void testSnakeCaseRenaming_data();
        void testSnakeCaseRenaming();
};

#endif
