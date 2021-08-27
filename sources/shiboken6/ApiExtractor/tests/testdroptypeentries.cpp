/****************************************************************************
**
** Copyright (C) 2016 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of the test suite of Qt for Python.
**
** $QT_BEGIN_LICENSE:GPL-EXCEPT$
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** GNU General Public License Usage
** Alternatively, this file may be used under the terms of the GNU
** General Public License version 3 as published by the Free Software
** Foundation with exceptions as appearing in the file LICENSE.GPL3-EXCEPT
** included in the packaging of this file. Please review the following
** information to ensure the GNU General Public License requirements will
** be met: https://www.gnu.org/licenses/gpl-3.0.html.
**
** $QT_END_LICENSE$
**
****************************************************************************/

#include "testdroptypeentries.h"
#include <QtTest/QTest>
#include "testutil.h"
#include <abstractmetaenum.h>
#include <abstractmetalang.h>
#include <typesystem.h>
#include <conditionalstreamreader.h>

static const char* cppCode ="\
    struct ValueA {};\n\
    struct ValueB {};\n\
    struct ObjectA {};\n\
    struct ObjectB {};\n\
    namespace NamespaceA {\n\
        struct InnerClassA {};\n\
        namespace InnerNamespaceA {}\n\
    }\n\
    namespace NamespaceB {}\n\
    enum EnumA { Value0 };\n\
    enum EnumB { Value1 };\n\
    void funcA();\n\
    void funcB();\n";

static const char* xmlCode = "\
<typesystem package='Foo'>\n\
    <value-type name='ValueA'/>\n\
    <value-type name='ValueB'/>\n\
    <object-type name='ObjectA'/>\n\
    <object-type name='ObjectB'/>\n\
    <namespace-type name='NamespaceA'>\n\
        <value-type name='InnerClassA'/>\n\
        <namespace-type name='InnerNamespaceA'/>\n\
    </namespace-type>\n\
    <namespace-type name='NamespaceB'/>\n\
    <enum-type name='EnumA'/>\n\
    <enum-type name='EnumB'/>\n\
    <function signature='funcA()'/>\n\
    <function signature='funcB()'/>\n\
</typesystem>\n";

void TestDropTypeEntries::testDropEntries()
{
    const QStringList droppedEntries{QLatin1String("Foo.ValueB"),
        QLatin1String("ObjectB"), // Check whether module can be omitted
        QLatin1String("Foo.NamespaceA.InnerClassA"),
        QLatin1String("Foo.NamespaceB"), QLatin1String("Foo.EnumB"),
        QLatin1String("Foo.funcB()"),
        QLatin1String("Foo.NamespaceA.InnerNamespaceA")};
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false,
                                                                QString(), droppedEntries));
    QVERIFY(!builder.isNull());

    AbstractMetaClassList classes = builder->classes();
    QVERIFY(AbstractMetaClass::findClass(classes, QLatin1String("ValueA")));
    QVERIFY(!AbstractMetaClass::findClass(classes, QLatin1String("ValueB")));
    QVERIFY(AbstractMetaClass::findClass(classes, QLatin1String("ObjectA")));
    QVERIFY(!AbstractMetaClass::findClass(classes, QLatin1String("ObjectB")));
    QVERIFY(AbstractMetaClass::findClass(classes, QLatin1String("NamespaceA")));
    QVERIFY(!AbstractMetaClass::findClass(classes, QLatin1String("NamespaceA::InnerClassA")));
    QVERIFY(!AbstractMetaClass::findClass(classes, QLatin1String("NamespaceB")));

    AbstractMetaEnumList globalEnums = builder->globalEnums();
    QCOMPARE(globalEnums.count(), 1);
    QCOMPARE(globalEnums.constFirst().name(), QLatin1String("EnumA"));

    TypeDatabase* td = TypeDatabase::instance();
    QVERIFY(td->findType(QLatin1String("funcA")));
    QVERIFY(!td->findType(QLatin1String("funcB")));
}

void TestDropTypeEntries::testDontDropEntries()
{
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(!builder.isNull());

    AbstractMetaClassList classes = builder->classes();
    QVERIFY(AbstractMetaClass::findClass(classes, QLatin1String("ValueA")));
    QVERIFY(AbstractMetaClass::findClass(classes, QLatin1String("ValueB")));
    QVERIFY(AbstractMetaClass::findClass(classes, QLatin1String("ObjectA")));
    QVERIFY(AbstractMetaClass::findClass(classes, QLatin1String("ObjectB")));
    QVERIFY(AbstractMetaClass::findClass(classes, QLatin1String("NamespaceA")));
    QVERIFY(AbstractMetaClass::findClass(classes, QLatin1String("NamespaceA::InnerClassA")));
    QVERIFY(AbstractMetaClass::findClass(classes, QLatin1String("NamespaceB")));

    QCOMPARE(builder->globalEnums().size(), 2);

    TypeDatabase* td = TypeDatabase::instance();
    QVERIFY(td->findType(QLatin1String("funcA")));
    QVERIFY(td->findType(QLatin1String("funcB")));
}

static const char* cppCode2 ="\
    struct ValueA {\n\
        void func();\n\
    };\n";

static const char* xmlCode2 = R"(
<typesystem package='Foo'>
    <value-type name='ValueA'>
        <modify-function signature='func()' remove='all'/>
    </value-type>
</typesystem>
)";

void TestDropTypeEntries::testDropEntryWithChildTags()
{
    QStringList droppedEntries(QLatin1String("Foo.ValueA"));
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode2, xmlCode2, false,
                                                                QString(), droppedEntries));
    QVERIFY(!builder.isNull());
    QVERIFY(!AbstractMetaClass::findClass(builder->classes(), QLatin1String("ValueA")));
}


void TestDropTypeEntries::testDontDropEntryWithChildTags()
{
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode2, xmlCode2, false));
    QVERIFY(!builder.isNull());
    QVERIFY(AbstractMetaClass::findClass(builder->classes(), QLatin1String("ValueA")));
}

void TestDropTypeEntries::testConditionalParsing_data()
{
    const QString xml = QStringLiteral(R"(<?xml version="1.0" encoding="UTF-8"?>
<root>
    <tag1>text</tag1>
    <?if keyword1?>
        <tag2>text</tag2>
        <?if keyword2?>
            <tag3>text</tag3>
        <?endif?>
        <?if keyword1 !keyword2?>
            <tag4>text</tag4>
        <?endif?>
    <?endif?>
    <tag5>text</tag5>
    <?if !keyword99?> <!-- Exclusion only -->
        <tag6>text</tag6>
    <?endif?>
</root>)");

    const QString root = QStringLiteral("root");
    const QString tag1 = QStringLiteral("tag1");
    const QString tag2 = QStringLiteral("tag2");
    const QString tag3 = QStringLiteral("tag3");
    const QString tag4 = QStringLiteral("tag4");
    const QString tag5 = QStringLiteral("tag5");
    const QString tag6 = QStringLiteral("tag6");
    const QString keyword1 = QStringLiteral("keyword1");
    const QString keyword2 = QStringLiteral("keyword2");

    QTest::addColumn<QString>("xml");
    QTest::addColumn<QStringList>("keywords");
    QTest::addColumn<QStringList>("expectedTags");

    QTest::newRow("no-keywords")
        << xml << QStringList{} << QStringList{root, tag1, tag5, tag6};

    QTest::newRow("skip-nested-condition")
        << xml << QStringList{keyword1}
        << QStringList{root, tag1, tag2, tag4, tag5, tag6};

    QTest::newRow("both/check-not")
        << xml << QStringList{keyword1, keyword2}
        << QStringList{root, tag1, tag2, tag3, tag5, tag6};
}

// Parse XML and return a list of tags encountered
static QStringList parseXml(const QString &xml, const QStringList &keywords)
{
    QStringList tags;
    ConditionalStreamReader reader(xml);
    reader.setConditions(keywords);
    while (!reader.atEnd()) {
        auto t = reader.readNext();
        switch (t) {
        case QXmlStreamReader::StartElement:
            tags.append(reader.name().toString());
            break;
        default:
            break;
        }
    }
    return tags;
}

void TestDropTypeEntries::testConditionalParsing()
{
    QFETCH(QString, xml);
    QFETCH(QStringList, keywords);
    QFETCH(QStringList, expectedTags);

    const QStringList actualTags = parseXml(xml, keywords);
    QCOMPARE(actualTags, expectedTags);
}

void TestDropTypeEntries::testEntityParsing()
{
    const QString xml = QStringLiteral(R"(<?xml version="1.0" encoding="UTF-8"?>
<root>
    <?entity testentity word1 word2?>
    <text>bla &testentity;</text>
</root>)");

    QString actual;
    ConditionalStreamReader reader(xml);
    while (!reader.atEnd()) {
        auto t = reader.readNext();
        switch (t) {
        case QXmlStreamReader::Characters:
            actual.append(reader.text());
        default:
            break;
        }
    }
    QVERIFY2(!reader.hasError(), qPrintable(reader.errorString()));
    QCOMPARE(actual.trimmed(), u"bla word1 word2");
}

QTEST_APPLESS_MAIN(TestDropTypeEntries)
