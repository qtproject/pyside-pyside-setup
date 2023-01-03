// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "testremoveimplconv.h"
#include "testutil.h"
#include <QtTest/QTest>
#include <abstractmetaargument.h>
#include <abstractmetafunction.h>
#include <abstractmetalang.h>
#include <abstractmetatype.h>
#include <complextypeentry.h>

// When a constructor able to trigger implicity conversions is removed
// it should not appear in the implicity conversion list.
void TestRemoveImplConv::testRemoveImplConv()
{
    const char cppCode[] = "\
    struct A {};\n\
    struct B {};\n\
    struct C {\n\
        C(const A&);\n\
        C(const B&);\n\
    };\n";
    const char xmlCode[] = "\
    <typesystem package=\"Foo\">\n\
        <value-type name='A'/>\n\
        <value-type name='B'/>\n\
        <value-type name='C'>\n\
            <modify-function signature='C(const A&amp;)' remove='all'/>\n\
        </value-type>\n\
    </typesystem>\n";
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    QCOMPARE(classes.size(), 3);
    const auto classA = AbstractMetaClass::findClass(classes, u"A");
    QVERIFY(classA);
    const auto classB = AbstractMetaClass::findClass(classes, u"B");
    QVERIFY(classB);
    const auto classC = AbstractMetaClass::findClass(classes, u"C");
    QVERIFY(classC);
    const auto implConv = classC->implicitConversions();
    QCOMPARE(implConv.size(), 1);
    QCOMPARE(implConv.constFirst()->arguments().constFirst().type().typeEntry(),
             classB->typeEntry());
}

QTEST_APPLESS_MAIN(TestRemoveImplConv)
