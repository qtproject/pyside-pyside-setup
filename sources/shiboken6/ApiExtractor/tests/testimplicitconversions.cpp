// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "testimplicitconversions.h"
#include "testutil.h"
#include <abstractmetaargument.h>
#include <abstractmetafunction.h>
#include <abstractmetalang.h>
#include <abstractmetatype.h>
#include <complextypeentry.h>
#include <QtTest/QTest>

void TestImplicitConversions::testWithPrivateCtors()
{
    const char cppCode[] = "\
    class B;\n\
    class C;\n\
    class A {\n\
        A(const B&);\n\
    public:\n\
        A(const C&);\n\
    };\n\
    class B {};\n\
    class C {};\n";
    const char xmlCode[] = "\
    <typesystem package='Foo'>\n\
        <value-type name='A'/>\n\
        <value-type name='B'/>\n\
        <value-type name='C'/>\n\
    </typesystem>\n";
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    QCOMPARE(classes.size(), 3);

    const auto classA = AbstractMetaClass::findClass(classes, u"A");
    const auto classC = AbstractMetaClass::findClass(classes, u"C");
    const auto implicitConvs = classA->implicitConversions();
    QCOMPARE(implicitConvs.size(), 1);
    QCOMPARE(implicitConvs.constFirst()->arguments().constFirst().type().typeEntry(),
             classC->typeEntry());
}

void TestImplicitConversions::testWithModifiedVisibility()
{
    const char cppCode[] = "\
    class B;\n\
    class A {\n\
    public:\n\
        A(const B&);\n\
    };\n\
    class B {};\n";
    const char xmlCode[] = R"(
<typesystem package='Foo'>
    <value-type name='A'>
        <modify-function signature='A(const B&amp;)' access='private'/>
    </value-type>
    <value-type name='B'/>
</typesystem>
)";
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    QCOMPARE(classes.size(), 2);
    const auto classA = AbstractMetaClass::findClass(classes, u"A");
    const auto classB = AbstractMetaClass::findClass(classes, u"B");
    const auto implicitConvs = classA->implicitConversions();
    QCOMPARE(implicitConvs.size(), 1);
    QCOMPARE(implicitConvs.constFirst()->arguments().constFirst().type().typeEntry(),
             classB->typeEntry());
}


void TestImplicitConversions::testWithAddedCtor()
{
    const char cppCode[] = "\
    class B;\n\
    class A {\n\
    public:\n\
        A(const B&);\n\
    };\n\
    class B {};\n\
    class C {};\n";
    const char xmlCode[] = "\
    <typesystem package='Foo'>\n\
        <custom-type name='TARGETLANGTYPE'/>\n\
        <value-type name='A'>\n\
            <add-function signature='A(const C&amp;)'/>\n\
        </value-type>\n\
        <value-type name='B'>\n\
            <add-function signature='B(TARGETLANGTYPE*)'/>\n\
        </value-type>\n\
        <value-type name='C'/>\n\
    </typesystem>\n";
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    QCOMPARE(classes.size(), 3);

    const auto classA = AbstractMetaClass::findClass(classes, u"A");
    auto implicitConvs = classA->implicitConversions();
    QCOMPARE(implicitConvs.size(), 2);

    // Added constructors with custom types should never result in implicit converters.
    const auto classB = AbstractMetaClass::findClass(classes, u"B");
    implicitConvs = classB->implicitConversions();
    QCOMPARE(implicitConvs.size(), 0);
}

void TestImplicitConversions::testWithExternalConversionOperator()
{
    const char cppCode[] = "\
    class A {};\n\
    struct B {\n\
        operator A() const;\n\
    };\n";
    const char xmlCode[] = "\n\
    <typesystem package='Foo'>\n\
        <value-type name='A'/>\n\
        <value-type name='B'/>\n\
    </typesystem>\n";
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    QCOMPARE(classes.size(), 2);
    const auto classA = AbstractMetaClass::findClass(classes, u"A");
    const auto classB = AbstractMetaClass::findClass(classes, u"B");
    const auto implicitConvs = classA->implicitConversions();
    QCOMPARE(implicitConvs.size(), 1);
    const auto &externalConvOps = classA->externalConversionOperators();
    QCOMPARE(externalConvOps.size(), 1);

    AbstractMetaFunctionCPtr convOp;
    for (const auto &func : classB->functions()) {
        if (func->isConversionOperator())
            convOp = func;
    }
    QVERIFY(convOp);
    QCOMPARE(implicitConvs.constFirst(), convOp);
}

QTEST_APPLESS_MAIN(TestImplicitConversions)
