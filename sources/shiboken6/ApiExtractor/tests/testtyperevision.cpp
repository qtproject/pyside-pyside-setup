// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "testtyperevision.h"
#include "testutil.h"
#include <abstractmetaenum.h>
#include <abstractmetalang.h>
#include <complextypeentry.h>
#include <enumtypeentry.h>
#include <flagstypeentry.h>
#include <typedatabase.h>

#include <qtcompat.h>

#include <QtTest/QTest>

using namespace Qt::StringLiterals;

void TestTypeRevision::testRevisionAttr()
{
    const char cppCode[] = "class Rev_0 {};"
                          "class Rev_1 {};"
                          "class Rev_2 { public: enum Rev_3 { X }; enum Rev_5 { Y }; };";
    const char xmlCode[] = "<typesystem package=\"Foo\">"
                        "<value-type name=\"Rev_0\"/>"
                        "<value-type name=\"Rev_1\" revision=\"1\"/>"
                        "<object-type name=\"Rev_2\" revision=\"2\">"
                        "    <enum-type name=\"Rev_3\" revision=\"3\" flags=\"Flag_4\" flags-revision=\"4\" />"
                        "    <enum-type name=\"Rev_5\" revision=\"5\" flags=\"Flag_5\" />"
                        "</object-type>"
                        "</typesystem>";
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    const auto rev0 = AbstractMetaClass::findClass(classes, u"Rev_0");
    QCOMPARE(rev0->typeEntry()->revision(), 0);

    const auto rev1 = AbstractMetaClass::findClass(classes, u"Rev_1");
    QCOMPARE(rev1->typeEntry()->revision(), 1);

    const auto rev2 = AbstractMetaClass::findClass(classes, u"Rev_2");
    QCOMPARE(rev2->typeEntry()->revision(), 2);

    auto rev3 = rev2->findEnum(u"Rev_3"_s);
    QVERIFY(rev3.has_value());
    QCOMPARE(rev3->typeEntry()->revision(), 3);
    auto rev4 = rev3->typeEntry()->flags();
    QCOMPARE(rev4->revision(), 4);
    auto rev5 = rev2->findEnum(u"Rev_5"_s);
    QVERIFY(rev5.has_value());
    EnumTypeEntryCPtr revEnumTypeEntry = rev5->typeEntry();
    QCOMPARE(revEnumTypeEntry->revision(), 5);
    QCOMPARE(revEnumTypeEntry->flags()->revision(), 5);
}


void TestTypeRevision::testVersion_data()
{
    QTest::addColumn<QString>("version");
    QTest::addColumn<int>("expectedClassCount");

    QTest::newRow("none") << QString() << 2;
    QTest::newRow("1.0") << QString::fromLatin1("1.0") << 1;  // Bar20 excluded
    QTest::newRow("2.0") << QString::fromLatin1("2.0") << 2;
    QTest::newRow("3.0") << QString::fromLatin1("3.0") << 1;  // Bar excluded by "until"
}

void TestTypeRevision::testVersion()
{
    QFETCH(QString, version);
    QFETCH(int, expectedClassCount);

    const char cppCode[] = R"CPP(
class Bar {};
class Bar20 {};
)CPP";
    const char xmlCode[] = R"XML(
<typesystem package="Foo">
    <value-type name="Bar" until="2.0"/>
    <value-type name="Bar20" since="2.0"/>
</typesystem>
)XML";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, true, version));
    QVERIFY(builder);

    QCOMPARE(builder->classes().size(), expectedClassCount);
}

QTEST_APPLESS_MAIN(TestTypeRevision)


