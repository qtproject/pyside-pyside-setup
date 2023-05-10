// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "testresolvetype.h"
#include "testutil.h"
#include <abstractmetaargument.h>
#include <abstractmetaenum.h>
#include <abstractmetafunction.h>
#include <abstractmetalang.h>
#include <abstractmetatype.h>
#include <complextypeentry.h>
#include <enumtypeentry.h>
#include <primitivetypeentry.h>
#include <typedatabase.h>

#include <qtcompat.h>

#include <QtTest/QTest>

using namespace Qt::StringLiterals;

void TestResolveType::initTestCase()
{
    // For enum lookup in testFixDefaultArguments()
    AbstractMetaBuilder::setCodeModelTestMode(true);
}

void TestResolveType::testResolveReturnTypeFromParentScope()
{
    const char cppCode[] = "\n\
    namespace A {\n\
        struct B {\n\
            struct C {};\n\
        };\n\
        struct D : public B::C {\n\
            C* foo = 0;\n\
            C* method();\n\
        };\n\
    };";
    const char xmlCode[] = R"XML(
    <typesystem package='Foo'>
        <namespace-type name='A'>
            <value-type name='B'>
                <value-type name='C'/>
            </value-type>
            <value-type name='D'/>
        </namespace-type>
    </typesystem>)XML";
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    const auto classD = AbstractMetaClass::findClass(classes, u"A::D");
    QVERIFY(classD);
    const auto meth = classD->findFunction(u"method");
    QVERIFY(meth);
    QVERIFY(meth);
}

// Helper classes and functions for testing default value fixing.
// Put the AbstractMetaBuilder into test fixture struct to avoid having
// to re-parse for each data row.

struct DefaultValuesFixture
{
    std::shared_ptr<AbstractMetaBuilder> builder;

    AbstractMetaType intType;
    AbstractMetaType stringType;
    AbstractMetaType classType;
    AbstractMetaType listType;
    AbstractMetaType enumType;
    AbstractMetaClassCPtr klass{};
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
    static const Enum DefaultValue = enumValue1;
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
    if (!fixture->builder)
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

    for (const auto &f : fixture->klass->findFunctions(u"Test"_s)) {
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

    auto listFunc = fixture->klass->findFunction(u"listFunc"_s);
    if (!listFunc || listFunc->arguments().size() != 1)
        return -3;
    fixture->listType = listFunc->arguments().constFirst().type();

    fixture->enumType = AbstractMetaType(fixture->klass->enums().constFirst().typeEntry());
    fixture->enumType.decideUsagePattern();

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
    QString expected = u"std::list<Namespace::Test>()"_s;
    QTest::newRow("list")
        << fixture << setupOk << fixture.listType
        << expected << expected;
    QTest::newRow("partially qualified list")
        << fixture << setupOk << fixture.listType
        << "std::list<Test>()" << expected;

    // Test field expansion
    expected = u"Namespace::Test::INT_FIELD_1"_s;
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
    expected = u"QLatin1String(Namespace::Test::CHAR_FIELD_1)"_s;
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
    expected = u"Namespace::Test(Namespace::Test::CHAR_FIELD_1)"_s;
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
    expected = u"Namespace::Test(Namespace::Test::Enum::enumValue1)"_s;
    QTest::newRow("self from qualified enum")
        << fixture << setupOk << fixture.classType
        << expected << expected;
    QTest::newRow("self from enum")
        << fixture << setupOk << fixture.classType
        << "Test(enumValue1)" << expected;

    // Don't qualify fields to "Test::Enum::DefaultValue"
    QTest::newRow("enum from static field")
        << fixture << setupOk << fixture.enumType
        << "DefaultValue" << u"Namespace::Test::DefaultValue"_s;
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

// Verify that the typedefs of the C++ 11 integer types (int32_t, ...)
// are seen by the C++ parser, otherwise they are handled as unknown
// primitive types, causing invalid code to be generated.
// (see BuilderPrivate::visitHeader(),
// sources/shiboken6/ApiExtractor/clangparser/clangbuilder.cpp).
void TestResolveType::testCppTypes()
{
    static const char cppCode[] =R"(
#include <cstdint>

class Test
{
public:
    explicit Test(int32_t v);
};
)";
    static const char xmlCode[] = R"(
<typesystem package="Foo">
    <value-type name='Test'/>
    <primitive-type name='int32_t'/>
</typesystem>
)";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    const auto testClass = AbstractMetaClass::findClass(classes, u"Test");
    QVERIFY(testClass);

    auto *tdb = TypeDatabase::instance();
    auto int32TEntry = tdb->findType(u"int32_t"_s);
    QVERIFY2(int32TEntry, "int32_t not found");
    QVERIFY(int32TEntry->isPrimitive());
    auto int32T = std::static_pointer_cast<const PrimitiveTypeEntry>(int32TEntry);
    auto basicType = basicReferencedTypeEntry(int32T);
    QVERIFY2(basicType != int32T,
             "Typedef for int32_t not found. Check the system include paths.");
}

QTEST_APPLESS_MAIN(TestResolveType)
