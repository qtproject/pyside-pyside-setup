// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TESTCONVERSIONRULE_H
#define TESTCONVERSIONRULE_H

#include <QtCore/QObject>

class TestConversionRuleTag : public QObject
{
    Q_OBJECT
private slots:
    void testConversionRuleTagWithFile();
    void testConversionRuleTagReplace();
    void testConversionRuleTagAdd();
    void testConversionRuleTagWithInsertTemplate();
};

#endif
