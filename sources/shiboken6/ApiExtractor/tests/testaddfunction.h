// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TESTADDFUNCTION_H
#define TESTADDFUNCTION_H
#include <QtCore/QObject>

class TestAddFunction : public QObject
{
    Q_OBJECT
private slots:
    void testParsingFuncNameAndConstness();
    void testAddFunction();
    void testAddFunctionConstructor();
    void testAddFunctionTagDefaultValues();
    void testAddFunctionCodeSnippets();
    void testAddFunctionWithoutParenteses();
    void testAddFunctionWithDefaultArgs();
    void testAddFunctionAtModuleLevel();
    void testAddFunctionWithVarargs();
    void testAddStaticFunction();
    void testAddGlobalFunction();
    void testAddFunctionWithApiVersion();
    void testModifyAddedFunction();
    void testAddFunctionOnTypedef();
    void testAddFunctionWithTemplateArg();
    void testAddFunctionTypeParser_data();
    void testAddFunctionTypeParser();
};

#endif
