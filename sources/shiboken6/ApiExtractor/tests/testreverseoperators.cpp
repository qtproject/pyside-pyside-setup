// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "testreverseoperators.h"
#include <QtTest/QTest>
#include "testutil.h"
#include <abstractmetaargument.h>
#include <abstractmetafunction.h>
#include <abstractmetalang.h>
#include <typesystem.h>
#include <clangparser/compilersupport.h>

#include <algorithm>

void TestReverseOperators::testReverseSum()
{
    const char cppCode[] = "struct A {\n\
            A& operator+(int);\n\
        };\n\
        A& operator+(int, const A&);";
    const char xmlCode[] = "\n\
    <typesystem package=\"Foo\">\n\
        <primitive-type name='int' />\n\
        <value-type name='A' />\n\
    </typesystem>";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    const auto classA = AbstractMetaClass::findClass(classes, u"A");
    QVERIFY(classA);
    QCOMPARE(classA->functions().size(), 4);

    AbstractMetaFunctionCPtr reverseOp;
    AbstractMetaFunctionCPtr normalOp;
    for (const auto &func : classA->functions()) {
        if (func->name() == u"operator+") {
            if (func->isReverseOperator())
                reverseOp = func;
            else
                normalOp = func;
        }
    }

    QVERIFY(normalOp);
    QVERIFY(!normalOp->isReverseOperator());
    QCOMPARE(normalOp->arguments().size(), 1);
    QVERIFY(reverseOp);
    QVERIFY(reverseOp->isReverseOperator());
    QCOMPARE(reverseOp->arguments().size(), 1);
}

void TestReverseOperators::testReverseSumWithAmbiguity()
{
    const char cppCode[] = "\n\
    struct A { A operator+(int); };\n\
    A operator+(int, const A&);\n\
    struct B {};\n\
    B operator+(const A&, const B&);\n\
    B operator+(const B&, const A&);\n\
    ";
    const char xmlCode[] = "\n\
    <typesystem package=\"Foo\">\n\
        <primitive-type name='int' />\n\
        <value-type name='A' />\n\
        <value-type name='B' />\n\
    </typesystem>";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    const auto classA = AbstractMetaClass::findClass(classes, u"A");
    QVERIFY(classA);
    QCOMPARE(classA->functions().size(), 4);

    const auto classB = AbstractMetaClass::findClass(classes, u"B");
    QVERIFY(classB);
    QCOMPARE(classB->functions().size(), 4);

    AbstractMetaFunctionCPtr reverseOp;
    AbstractMetaFunctionCPtr normalOp;
    for (const auto &func : classB->functions()) {
        if (func->name() == u"operator+") {
            if (func->isReverseOperator())
                reverseOp = func;
            else
                normalOp = func;
        }
    }
    QVERIFY(normalOp);
    QVERIFY(!normalOp->isReverseOperator());
    QCOMPARE(normalOp->arguments().size(), 1);
    QCOMPARE(normalOp->minimalSignature(), u"operator+(B,A)");
    QVERIFY(reverseOp);
    QVERIFY(reverseOp->isReverseOperator());
    QCOMPARE(reverseOp->arguments().size(), 1);
    QCOMPARE(reverseOp->minimalSignature(), u"operator+(A,B)");
}

void  TestReverseOperators::testSpaceshipOperator()
{
    const char cppCode[] = R"(
    class Test {
        public:
        explicit Test(int v);
        int operator<=>(const Test &rhs) const = default;
    };)";
    const char xmlCode[] = R"(
        <typesystem package="Foo">
            <value-type name='Test'/>
        </typesystem>)";
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false,
                                                                {}, {}, LanguageLevel::Cpp20));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    QCOMPARE(classes.size(), 1);
    const auto testClass = AbstractMetaClass::findClass(classes, u"Test");
    QVERIFY(testClass);
    const auto &functions = testClass->functions();
    // 6 operators should be synthesized
    const auto count = std::count_if(functions.cbegin(), functions.cend(),
                                     [](const AbstractMetaFunctionCPtr &f) {
                                         return f->isComparisonOperator();
                                     });
    QCOMPARE(count, 6);
}

QTEST_APPLESS_MAIN(TestReverseOperators)

