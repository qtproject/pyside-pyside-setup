// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TESTNAMESPACE_H
#define TESTNAMESPACE_H

#include <QtCore/QObject>

// The class is named 'NamespaceTest' to avoid clashes with Qt COIN using
// '-qtnamespace TestNamespace'.
class NamespaceTest : public QObject
{
    Q_OBJECT
    private slots:
        void testNamespaceMembers();
        void testNamespaceInnerClassMembers();
};

#endif
