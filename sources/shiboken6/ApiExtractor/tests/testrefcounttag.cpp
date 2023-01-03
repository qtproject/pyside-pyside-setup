// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "testrefcounttag.h"
#include "testutil.h"
#include <abstractmetafunction.h>
#include <abstractmetalang.h>
#include <modifications.h>

#include <qtcompat.h>

#include <QtTest/QTest>

using namespace Qt::StringLiterals;

void TestRefCountTag::testReferenceCountTag()
{
    const char cppCode[] = "\
    struct A {};\n\
    struct B {\n\
        void keepObject(B* b);\n\
    };\n";
    const char xmlCode[] = "\
    <typesystem package=\"Foo\">\n\
        <object-type name='A'/>\n\
        <object-type name='B'>\n\
        <modify-function signature='keepObject(B*)'>\n\
            <modify-argument index='1'>\n\
                <reference-count action='add'/>\n\
            </modify-argument>\n\
        </modify-function>\n\
        </object-type>\n\
    </typesystem>\n";
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    const auto classB = AbstractMetaClass::findClass(classes, u"B");
    const auto func = classB->findFunction(u"keepObject");
    QVERIFY(func);
    const auto refCount =
        func->modifications().constFirst().argument_mods().constFirst().referenceCounts().constFirst();
    QCOMPARE(refCount.action, ReferenceCount::Add);
}

void TestRefCountTag::testWithApiVersion()
{
    const char cppCode[] = "\
    struct A {};\n\
    struct B {\n\
        void keepObject(B*, B*);\n\
    };\n";
    const char xmlCode[] = "\
    <typesystem package=\"Foo\">\n\
        <object-type name='A'/>\n\
        <object-type name='B'>\n\
        <modify-function signature='keepObject(B*, B*)'>\n\
            <modify-argument index='1' since='0.1'>\n\
                <reference-count action='add'/>\n\
            </modify-argument>\n\
            <modify-argument index='2' since='0.2'>\n\
                <reference-count action='add'/>\n\
            </modify-argument>\n\
        </modify-function>\n\
        </object-type>\n\
    </typesystem>\n";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode,
                                                                false, u"0.1"_s));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    const auto classB = AbstractMetaClass::findClass(classes, u"B");
    const auto func = classB->findFunction(u"keepObject");
    QVERIFY(func);
    const auto refCount =
        func->modifications().constFirst().argument_mods().constFirst().referenceCounts().constFirst();
    QCOMPARE(refCount.action, ReferenceCount::Add);

    QCOMPARE(func->modifications().size(), 1);
}


QTEST_APPLESS_MAIN(TestRefCountTag)


