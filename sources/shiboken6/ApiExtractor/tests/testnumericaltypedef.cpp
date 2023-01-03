// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "testnumericaltypedef.h"
#include <QtTest/QTest>
#include "testutil.h"
#include <abstractmetaargument.h>
#include <abstractmetafunction.h>
#include <abstractmetalang.h>
#include <abstractmetatype.h>
#include <typesystem.h>

void TestNumericalTypedef::testNumericalTypedef()
{
    const char cppCode[] = "\
    typedef double real;\n\
    void funcDouble(double);\n\
    void funcReal(real);\n";
    const char xmlCode[] = "\
    <typesystem package='Foo'>\n\
        <primitive-type name='double'/>\n\
        <primitive-type name='real'/>\n\
        <function signature='funcDouble(double)'/>\n\
        <function signature='funcReal(real)'/>\n\
    </typesystem>\n";
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(builder);

    QCOMPARE(builder->globalFunctions().size(), 2);
    auto funcDouble = builder->globalFunctions().constFirst();
    auto funcReal = builder->globalFunctions().constLast();
    QVERIFY(funcReal);

    if (funcDouble->name() == u"funcReal")
        std::swap(funcDouble, funcReal);

    QCOMPARE(funcDouble->minimalSignature(), u"funcDouble(double)");
    QCOMPARE(funcReal->minimalSignature(), u"funcReal(real)");

    const AbstractMetaType doubleType = funcDouble->arguments().constFirst().type();
    QCOMPARE(doubleType.cppSignature(), u"double");
    QVERIFY(doubleType.isPrimitive());
    QVERIFY(isCppPrimitive(doubleType.typeEntry()));

    const AbstractMetaType realType = funcReal->arguments().constFirst().type();
    QCOMPARE(realType.cppSignature(), u"real");
    QVERIFY(realType.isPrimitive());
    QVERIFY(isCppPrimitive(realType.typeEntry()));
}

void TestNumericalTypedef::testUnsignedNumericalTypedef()
{
    const char cppCode[] = "\
    typedef unsigned short custom_ushort;\n\
    void funcUnsignedShort(unsigned short);\n\
    void funcUShort(custom_ushort);\n";
    const char xmlCode[] = "\
    <typesystem package='Foo'>\n\
        <primitive-type name='short'/>\n\
        <primitive-type name='unsigned short'/>\n\
        <primitive-type name='custom_ushort'/>\n\
        <function signature='funcUnsignedShort(unsigned short)'/>\n\
        <function signature='funcUShort(custom_ushort)'/>\n\
    </typesystem>\n";
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(builder);

    QCOMPARE(builder->globalFunctions().size(), 2);
    auto funcUnsignedShort = builder->globalFunctions().constFirst();
    auto funcUShort = builder->globalFunctions().constLast();

    if (funcUnsignedShort->name() == u"funcUShort")
        std::swap(funcUnsignedShort, funcUShort);

    QCOMPARE(funcUnsignedShort->minimalSignature(), u"funcUnsignedShort(unsigned short)");
    QCOMPARE(funcUShort->minimalSignature(), u"funcUShort(custom_ushort)");

    const AbstractMetaType unsignedShortType = funcUnsignedShort->arguments().constFirst().type();
    QCOMPARE(unsignedShortType.cppSignature(), u"unsigned short");
    QVERIFY(unsignedShortType.isPrimitive());
    QVERIFY(isCppPrimitive(unsignedShortType.typeEntry()));

    const AbstractMetaType ushortType = funcUShort->arguments().constFirst().type();
    QCOMPARE(ushortType.cppSignature(), u"custom_ushort");
    QVERIFY(ushortType.isPrimitive());
    QVERIFY(isCppPrimitive(ushortType.typeEntry()));
}

QTEST_APPLESS_MAIN(TestNumericalTypedef)

