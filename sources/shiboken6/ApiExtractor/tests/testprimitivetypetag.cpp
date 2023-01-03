// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "testprimitivetypetag.h"
#include "testutil.h"
#include <abstractmetalang.h>
#include <primitivetypeentry.h>

#include <qtcompat.h>

#include <QtTest/QTest>

using namespace Qt::StringLiterals;

void TestPrimitiveTypeTag::testPrimitiveTypeDefaultConstructor()
{
    const char cppCode[] = "\
    struct A {};\n\
    struct B {};\n";
    const char xmlCode[] = "\
    <typesystem package=\"Foo\">\n\
        <primitive-type name='A' default-constructor='A()'/>\n\
        <object-type name='B'/>\n\
    </typesystem>\n";
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(builder);

    AbstractMetaClassList classes = builder->classes();
    QCOMPARE(classes.size(), 1);
    const auto classB = AbstractMetaClass::findClass(classes, u"B");
    QVERIFY(classB);

    auto typeEntry = TypeDatabase::instance()->findPrimitiveType(u"A"_s);
    QVERIFY(typeEntry);
    QVERIFY(typeEntry->hasDefaultConstructor());
    QCOMPARE(typeEntry->defaultConstructor(), u"A()");
}

QTEST_APPLESS_MAIN(TestPrimitiveTypeTag)

