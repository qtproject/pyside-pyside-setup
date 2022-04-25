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

#include "testresolvetype.h"
#include <QtTest/QTest>
#include "testutil.h"
#include <abstractmetafunction.h>
#include <abstractmetalang.h>
#include <abstractmetatype.h>
#include <typesystem.h>

void TestResolveType::initTestCase()
{
    // For enum lookup in testFixDefaultArguments()
    AbstractMetaBuilder::setCodeModelTestMode(true);
}

void TestResolveType::testResolveReturnTypeFromParentScope()
{
    const char* cppCode = "\n\
    namespace A {\n\
        struct B {\n\
            struct C {};\n\
        };\n\
        struct D : public B::C {\n\
            C* foo = 0;\n\
            C* method();\n\
        };\n\
    };";
    const char* xmlCode = R"XML(
    <typesystem package='Foo'>
        <namespace-type name='A'>
            <value-type name='B'>
                <value-type name='C'/>
            </value-type>
            <value-type name='D'/>
        </namespace-type>
    </typesystem>)XML";
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(!builder.isNull());
    AbstractMetaClassList classes = builder->classes();
    const AbstractMetaClass *classD = AbstractMetaClass::findClass(classes, u"A::D");
    QVERIFY(classD);
    const auto meth = classD->findFunction(u"method");
    QVERIFY(!meth.isNull());
    QVERIFY(meth);
}

// Helper classes and functions for testing default value fixing.
// Put the AbstractMetaBuilder into test fixture struct to avoid having
// to re-parse for each data row.

struct DefaultValuesFixture
{
    QSharedPointer<AbstractMetaBuilder> builder;

    AbstractMetaType intType;
    AbstractMetaType stringType;
    AbstractMetaType classType;
    AbstractMetaType listType;
    const AbstractMetaClass *klass{};
};

Q_DECLARE_METATYPE(DefaultValuesFixture)
Q_DECLARE_METATYPE(AbstractMetaType)

static int populateDefaultValuesFixture(DefaultValuesFixture *fixture)
{
    static const char cppCode[] =R"(
#include <string>
#include <list>

namespace Namespace {
class Test
{
public:
    enum Enum { enumValue1, enumValue2 };

    explicit Test(int x = INT_FIELD_1);
    explicit Test(const std::string &t = std::string(CHAR_FIELD_1));

    static void listFunc(std::list<Test> list = std::list<Test>());

    static const int INT_FIELD_1 = 42;
    static const char *CHAR_FIELD_1;
};
} // Namespace
)";
    static const char xmlCode[] = R"(
<typesystem package="Foo">
    <namespace-type name='Namespace'>
        <value-type name='Test'>
            <enum-type name='Enum'/>
        </value-type>
    </namespace-type>
    <container-type name="std::list" type="list"/>
</typesystem>
)";

    fixture->builder.reset(TestUtil::parse(cppCode, xmlCode, false));
    if (fixture->builder.isNull())
        return -1;

    for (const auto &klass : fixture->builder->classes()) {
        if (klass->name() == u"Test") {
            fixture->klass = klass;
            break;
        }
    }
    if (!fixture->klass)
        return -2;

    fixture->classType = AbstractMetaType(fixture->klass->typeEntry());
    fixture->classType.decideUsagePattern();

    for (const auto &f : fixture->klass->findFunctions(u"Test"_qs)) {
        if (f->functionType() == AbstractMetaFunction::ConstructorFunction
            && f->arguments().size() == 1) {
            const auto type = f->arguments().constFirst().type();
            if (type.name() == u"int")
                fixture->intType = type;
            else
                fixture->stringType = type;
        }
    }
    if (fixture->intType.isVoid() || fixture->stringType.isVoid())
        return -3;

    auto listFunc = fixture->klass->findFunction(u"listFunc"_qs);
    if (listFunc.isNull() || listFunc->arguments().size() != 1)
        return -3;
    fixture->listType = listFunc->arguments().constFirst().type();

    return 0;
}

void TestResolveType::testFixDefaultArguments_data()
{
    DefaultValuesFixture fixture;
    const int setupOk = populateDefaultValuesFixture(&fixture);

    QTest::addColumn<DefaultValuesFixture>("fixture");
    QTest::addColumn<int>("setupOk"); // To verify setup
    QTest::addColumn<AbstractMetaType>("metaType"); // Type and parameters for fixup
    QTest::addColumn<QString>("input");
    QTest::addColumn<QString>("expected");

    QTest::newRow("int") << fixture << setupOk
        << fixture.intType << "1" << "1";
    QTest::newRow("int-macro") << fixture << setupOk
        << fixture.intType << "GL_MACRO" << "GL_MACRO";
    QTest::newRow("int-enum") << fixture << setupOk
        << fixture.intType << "enumValue1" << "Namespace::Test::Enum::enumValue1";

    // Test expansion of container types
    QString expected = u"std::list<Namespace::Test>()"_qs;
    QTest::newRow("list")
        << fixture << setupOk << fixture.listType
        << expected << expected;
    QTest::newRow("partially qualified list")
        << fixture << setupOk << fixture.listType
        << "std::list<Test>()" << expected;

    // Test field expansion
    expected = u"Namespace::Test::INT_FIELD_1"_qs;
    QTest::newRow("qualified class field")
        << fixture << setupOk << fixture.intType
        << expected << expected;
    QTest::newRow("partially qualified class field")
        << fixture << setupOk << fixture.intType
        << "Test::INT_FIELD_1" << expected;
    QTest::newRow("unqualified class field")
        << fixture << setupOk << fixture.intType
        << "INT_FIELD_1" << expected;

    // Test field expansion when constructing some class
    expected = u"QLatin1String(Namespace::Test::CHAR_FIELD_1)"_qs;
    QTest::newRow("class from qualified class field")
        << fixture << setupOk << fixture.classType
        << expected << expected;
    QTest::newRow("class from partially qualified class field")
        << fixture << setupOk << fixture.classType
        << "QLatin1String(Test::CHAR_FIELD_1)" << expected;
    QTest::newRow("class from unqualified class field")
        << fixture << setupOk << fixture.classType
        << "QLatin1String(CHAR_FIELD_1)" << expected;

    // Test field expansion when constructing class itself
    expected = u"Namespace::Test(Namespace::Test::CHAR_FIELD_1)"_qs;
    QTest::newRow("self from qualified class field")
        << fixture << setupOk << fixture.classType
        << expected << expected;
    QTest::newRow("self from partially qualified class field")
        << fixture << setupOk << fixture.classType
        << "Test(Test::CHAR_FIELD_1)" << expected;
    QTest::newRow("self from unqualified class field")
        << fixture << setupOk << fixture.classType
        << "Test(CHAR_FIELD_1)" << expected;

    // Test enum expansion when constructing class itself
    expected = u"Namespace::Test(Namespace::Test::Enum::enumValue1)"_qs;
    QTest::newRow("self from qualified enum")
        << fixture << setupOk << fixture.classType
        << expected << expected;
    QTest::newRow("self from enum")
        << fixture << setupOk << fixture.classType
        << "Test(enumValue1)" << expected;
}

void TestResolveType::testFixDefaultArguments()
{
    QFETCH(DefaultValuesFixture, fixture);
    QFETCH(int, setupOk);
    QFETCH(AbstractMetaType, metaType);
    QFETCH(QString, input);
    QFETCH(QString, expected);
    QCOMPARE(setupOk, 0);
    const QString actual = fixture.builder->fixDefaultValue(input, metaType, fixture.klass);
    QCOMPARE(actual, expected);
}

QTEST_APPLESS_MAIN(TestResolveType)

