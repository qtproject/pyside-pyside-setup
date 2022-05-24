// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TESTFUNCTIONTAG_H
#define TESTFUNCTIONTAG_H

#include <QtCore/QObject>

class TestFunctionTag : public QObject
{
    Q_OBJECT
private slots:
    void testFunctionTagForSpecificSignature();
    void testFunctionTagForAllSignatures();
    void testRenameGlobalFunction();
};

#endif
