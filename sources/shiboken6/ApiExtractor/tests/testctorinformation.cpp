// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "testctorinformation.h"
#include "abstractmetabuilder.h"
#include <QtTest/QTest>
#include "testutil.h"
#include <abstractmetalang.h>
#include <typesystem.h>

void TestCtorInformation::testCtorIsPrivate()
{
    const char cppCode[] = "class Control { public: Control() {} };\n\
                           class Subject { private: Subject() {} };\n\
                           class CtorLess { };\n";
    const char xmlCode[] = "<typesystem package='Foo'>\n\
                                <value-type name='Control'/>\n\
                                <object-type name='Subject'/>\n\
                                <value-type name='CtorLess'/>\n\
                           </typesystem>\n";
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    QCOMPARE(classes.size(), 3);
    auto klass = AbstractMetaClass::findClass(classes, u"Control");
    QVERIFY(klass);
    QVERIFY(klass->hasNonPrivateConstructor());
    klass = AbstractMetaClass::findClass(classes, u"Subject");
    QVERIFY(klass);
    QVERIFY(!klass->hasNonPrivateConstructor());
    klass = AbstractMetaClass::findClass(classes, u"CtorLess");
    QVERIFY(klass);
    QVERIFY(klass->hasNonPrivateConstructor());
}

void TestCtorInformation::testHasNonPrivateCtor()
{
    const char cppCode[] = "template<typename T>\n\
                           struct Base { Base(double) {} };\n\
                           typedef Base<int> Derived;\n";
    const char xmlCode[] = "<typesystem package='Foo'>\n\
                                <primitive-type name='int'/>\n\
                                <primitive-type name='double'/>\n\
                                <object-type name='Base' generate='no'/>\n\
                                <object-type name='Derived'/>\n\
                           </typesystem>\n";
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    QCOMPARE(classes.size(), 2);
    const auto base = AbstractMetaClass::findClass(classes, u"Base");
    QCOMPARE(base->hasNonPrivateConstructor(), true);
    const auto derived = AbstractMetaClass::findClass(classes, u"Derived");
    QCOMPARE(derived->hasNonPrivateConstructor(), true);
}

QTEST_APPLESS_MAIN(TestCtorInformation)
