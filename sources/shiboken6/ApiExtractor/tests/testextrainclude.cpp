// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "testextrainclude.h"
#include <QtTest/QTest>
#include "testutil.h"
#include <abstractmetalang.h>
#include <complextypeentry.h>
#include <typesystemtypeentry.h>

void TestExtraInclude::testClassExtraInclude()
{
    const char cppCode[] = "struct A {};\n";
    const char xmlCode[] = "\
    <typesystem package='Foo'>\n\
        <value-type name='A'>\n\
            <extra-includes>\n\
                <include file-name='header.h' location='global'/>\n\
            </extra-includes>\n\
        </value-type>\n\
    </typesystem>\n";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    const auto classA = AbstractMetaClass::findClass(classes, u"A");
    QVERIFY(classA);

    QList<Include> includes = classA->typeEntry()->extraIncludes();
    QCOMPARE(includes.size(), 1);
    QCOMPARE(includes.constFirst().name(), u"header.h");
}

void TestExtraInclude::testGlobalExtraIncludes()
{
    const char cppCode[] = "struct A {};\n";
    const char xmlCode[] = "\
    <typesystem package='Foo'>\n\
        <extra-includes>\n\
            <include file-name='header1.h' location='global'/>\n\
            <include file-name='header2.h' location='global'/>\n\
        </extra-includes>\n\
        <value-type name='A'/>\n\
    </typesystem>\n";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    QVERIFY(AbstractMetaClass::findClass(classes, u"A"));

    auto *td = TypeDatabase::instance();
    TypeSystemTypeEntryCPtr module = td->defaultTypeSystemType();
    QVERIFY(module);
    QCOMPARE(module->name(), u"Foo");

    QList<Include> includes = module->extraIncludes();
    QCOMPARE(includes.size(), 2);
    QCOMPARE(includes.constFirst().name(), u"header1.h");
    QCOMPARE(includes.constLast().name(), u"header2.h");
}

QTEST_APPLESS_MAIN(TestExtraInclude)
