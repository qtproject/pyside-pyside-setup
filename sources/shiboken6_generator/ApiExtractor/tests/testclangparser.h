// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TESTCLANGPARSER_H
#define TESTCLANGPARSER_H

#include <QtCore/qobject.h>

class TestClangParser : public QObject
{
    Q_OBJECT
private slots:
    void testClangTypeParsing_data();
    void testClangTypeParsing();
    void testFunctionPointers();
    void testParseTriplet_data();
    void testParseTriplet();
};

#endif // TESTCLANGPARSER_H
