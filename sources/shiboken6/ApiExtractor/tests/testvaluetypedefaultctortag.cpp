// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "testvaluetypedefaultctortag.h"
#include <QtTest/QTest>
#include "testutil.h"
#include <abstractmetalang.h>
#include <complextypeentry.h>

void TestValueTypeDefaultCtorTag::testValueTypeDefaultCtorTagArgument()
{
    const char cppCode[] = "\n\
    struct A {\n\
        A(int,int);\n\
    };\n\
    struct B {};\n\
    ";
    const char xmlCode[] = "\n\
    <typesystem package='Foo'>\n\
        <primitive-type name='int' />\n\
        <value-type name='A' default-constructor='A(0, 0)' />\n\
        <value-type name='B' />\n\
    </typesystem>";
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(builder);

    AbstractMetaClassList classes = builder->classes();

    const auto classA = AbstractMetaClass::findClass(classes, u"A");
    QVERIFY(classA);
    QVERIFY(classA->typeEntry()->hasDefaultConstructor());
    QCOMPARE(classA->typeEntry()->defaultConstructor(), u"A(0, 0)");

    const auto classB = AbstractMetaClass::findClass(classes, u"B");
    QVERIFY(classB);
    QVERIFY(!classB->typeEntry()->hasDefaultConstructor());
}

QTEST_APPLESS_MAIN(TestValueTypeDefaultCtorTag)
