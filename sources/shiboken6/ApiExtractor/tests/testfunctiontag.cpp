// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "testfunctiontag.h"
#include "testutil.h"
#include <abstractmetafunction.h>
#include <modifications.h>
#include <typesystem.h>

#include <qtcompat.h>

#include <QtTest/QTest>

using namespace Qt::StringLiterals;

void TestFunctionTag::testFunctionTagForSpecificSignature()
{
    const char cppCode[] = "void globalFunction(int); void globalFunction(float); void dummy();\n";
    const char xmlCode[] = "\
    <typesystem package=\"Foo\">\n\
        <primitive-type name='int'/>\n\
        <primitive-type name='float'/>\n\
        <function signature='globalFunction(int)'/>\n\
    </typesystem>\n";
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(builder);

    TypeEntryCPtr func = TypeDatabase::instance()->findType(u"globalFunction"_s);
    QVERIFY(func);
    QCOMPARE(builder->globalFunctions().size(), 1);
}

void TestFunctionTag::testFunctionTagForAllSignatures()
{
    const char cppCode[] = "void globalFunction(int); void globalFunction(float); void dummy();\n";
    const char xmlCode[] = "\
    <typesystem package=\"Foo\">\n\
        <primitive-type name='int'/>\n\
        <primitive-type name='float'/>\n\
        <function signature='globalFunction(int)'/>\n\
        <function signature='globalFunction(float)'/>\n\
    </typesystem>\n";
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(builder);

    TypeEntryCPtr func = TypeDatabase::instance()->findType(u"globalFunction"_s);
    QVERIFY(func);
    QCOMPARE(builder->globalFunctions().size(), 2);
}

void TestFunctionTag::testRenameGlobalFunction()
{
    const char cppCode[] = "void global_function_with_ugly_name();\n";
    const char xmlCode[] = "\
    <typesystem package='Foo'>\n\
        <function signature='global_function_with_ugly_name()' rename='smooth'/>\n\
    </typesystem>\n";
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(builder);

    TypeEntryCPtr func = TypeDatabase::instance()->findType(u"global_function_with_ugly_name"_s);
    QVERIFY(func);

    QCOMPARE(builder->globalFunctions().size(), 1);
    const auto metaFunc = builder->globalFunctions().constFirst();

    QVERIFY(metaFunc);
    QCOMPARE(metaFunc->modifications().size(), 1);
    QVERIFY(metaFunc->modifications().constFirst().isRenameModifier());
    QCOMPARE(metaFunc->modifications().constFirst().renamedToName(),
             u"smooth");

    QCOMPARE(metaFunc->name(), u"smooth");
    QCOMPARE(metaFunc->originalName(), u"global_function_with_ugly_name");
    QCOMPARE(metaFunc->minimalSignature(), u"global_function_with_ugly_name()");
}

QTEST_APPLESS_MAIN(TestFunctionTag)

