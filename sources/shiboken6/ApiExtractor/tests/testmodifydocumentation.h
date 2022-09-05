// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TESTMODIFYDOCUMENTATION_H
#define TESTMODIFYDOCUMENTATION_H

#include <QtCore/QObject>

class TestModifyDocumentation : public QObject
{
Q_OBJECT
private slots:
    void testModifyDocumentation();
    void testInjectAddedFunctionDocumentation();
};

#endif
