// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "testvoidarg.h"
#include <QtTest/QTest>
#include "testutil.h"
#include <abstractmetaargument.h>
#include <abstractmetafunction.h>
#include <abstractmetalang.h>
#include <typesystem.h>

void TestVoidArg::testVoidParsedFunction()
{
    const char cppCode[] = "struct A { void a(void); };";
    const char xmlCode[] = "\n\
    <typesystem package=\"Foo\">\n\
        <value-type name='A'/>\n\
    </typesystem>";
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    const auto classA = AbstractMetaClass::findClass(classes, u"A");
    QVERIFY(classA);
    const auto addedFunc = classA->findFunction(u"a");
    QVERIFY(addedFunc);
    QCOMPARE(addedFunc->arguments().size(), 0);
}

void TestVoidArg::testVoidAddedFunction()
{
    const char cppCode[] = "struct A { };";
    const char xmlCode[] = "\n\
    <typesystem package=\"Foo\">\n\
        <value-type name='A' >\n\
            <add-function signature=\"a(void)\"/>\n\
        </value-type>\n\
    </typesystem>";
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    const auto classA = AbstractMetaClass::findClass(classes, u"A");
    QVERIFY(classA);
    const auto addedFunc = classA->findFunction(u"a");
    QVERIFY(addedFunc);
    QCOMPARE(addedFunc->arguments().size(), 0);

}

void TestVoidArg::testVoidPointerParsedFunction()
{
    const char cppCode[] = "struct A { void a(void*); };";
    const char xmlCode[] = "\n\
    <typesystem package=\"Foo\">\n\
        <value-type name='A' />\n\
    </typesystem>";
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    const auto classA = AbstractMetaClass::findClass(classes, u"A");
    QVERIFY(classA);
    const auto addedFunc = classA->findFunction(u"a");
    QVERIFY(addedFunc);
    QCOMPARE(addedFunc->arguments().size(), 1);

}

QTEST_APPLESS_MAIN(TestVoidArg)
