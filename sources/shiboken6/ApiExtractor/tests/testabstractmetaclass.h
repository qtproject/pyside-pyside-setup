// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TESTABSTRACTMETACLASS_H
#define TESTABSTRACTMETACLASS_H

#include <QtCore/QObject>

class AbstractMetaBuilder;

class TestAbstractMetaClass : public QObject
{
    Q_OBJECT
private slots:
    void testClassName();
    void testClassNameUnderNamespace();
    void testVirtualMethods();
    void testVirtualBase();
    void testDefaultValues();
    void testModifiedDefaultValues();
    void testInnerClassOfAPolymorphicOne();
    void testForwardDeclaredInnerClass();
    void testSpecialFunctions();
    void testClassDefaultConstructors();
    void testClassInheritedDefaultConstructors();
    void testAbstractClassDefaultConstructors();
    void testObjectTypesMustNotHaveCopyConstructors();
    void testIsPolymorphic();
    void testClassTypedefedBaseClass();
    void testFreeOperators_data();
    void testFreeOperators();
    void testUsingMembers();
    void testUsingTemplateMembers_data();
    void testUsingTemplateMembers();
    void testGenerateFunctions();
};

#endif // TESTABSTRACTMETACLASS_H
