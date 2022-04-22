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

#include "testenum.h"
#include <QtTest/QTest>
#include "testutil.h"
#include <abstractmetaenum.h>
#include <abstractmetafunction.h>
#include <abstractmetalang.h>
#include <abstractmetabuilder_p.h>
#include <typesystem.h>
#include <parser/enumvalue.h>

void TestEnum::testEnumCppSignature()
{
    const char* cppCode ="\
    enum GlobalEnum { A, B };\n\
    \n\
    struct A {\n\
        enum ClassEnum { CA, CB };\n\
        void method(ClassEnum);\n\
    };\n\
    void func(A::ClassEnum);\n";
    const char* xmlCode = "\
    <typesystem package=\"Foo\">\n\
        <enum-type name='GlobalEnum'/>\n\
        <value-type name='A'>\n\
            <enum-type name='ClassEnum'/>\n\
        </value-type>\n\
        <function signature='func(A::ClassEnum)'/>\n\
    </typesystem>\n";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode));
    QVERIFY(!builder.isNull());
    AbstractMetaClassList classes = builder->classes();
    QCOMPARE(classes.size(), 1);

    AbstractMetaEnumList globalEnums = builder->globalEnums();
    QCOMPARE(globalEnums.size(), 1);
    QCOMPARE(globalEnums.constFirst().name(), u"GlobalEnum");

    // enum as parameter of a function
    const auto functions = builder->globalFunctions();
    QCOMPARE(functions.size(), 1);
    QCOMPARE(functions.constFirst()->arguments().size(), 1);
    QCOMPARE(functions.constFirst()->arguments().constFirst().type().cppSignature(),
             u"A::ClassEnum");

    // enum as parameter of a method
    const AbstractMetaClass *classA = AbstractMetaClass::findClass(classes, QLatin1String("A"));
    QCOMPARE(classA->enums().size(), 1);
    const auto funcs = classA->queryFunctionsByName(QLatin1String("method"));
    QVERIFY(!funcs.isEmpty());
    const auto method = funcs.constFirst();
    AbstractMetaArgument arg = method->arguments().constFirst();
    QCOMPARE(arg.type().name(), u"ClassEnum");
    QCOMPARE(arg.type().cppSignature(), u"A::ClassEnum");
    QCOMPARE(functions.constFirst()->arguments().size(), 1);
    arg = functions.constFirst()->arguments().constFirst();
    QCOMPARE(arg.type().name(), u"ClassEnum");
    QCOMPARE(arg.type().cppSignature(), u"A::ClassEnum");

    AbstractMetaEnumList classEnums = classA->enums();
    QVERIFY(!classEnums.isEmpty());
    QCOMPARE(classEnums.constFirst().name(), u"ClassEnum");
    auto e = AbstractMetaClass::findEnumValue(classes, QLatin1String("CA"));
    QVERIFY(e.has_value());
    e = AbstractMetaClass::findEnumValue(classes, QLatin1String("ClassEnum::CA"));
    QVERIFY(e.has_value());
}

void TestEnum::testEnumWithApiVersion()
{
    const char* cppCode ="\
    struct A {\n\
        enum ClassEnum { EnumA, EnumB };\n\
        enum ClassEnum2 { EnumC, EnumD };\n\
    };\n";
    const char* xmlCode = "\
    <typesystem package=\"Foo\">\n\
        <value-type name='A'>\n\
            <enum-type name='ClassEnum' since='0.1'/>\n\
            <enum-type name='ClassEnum2' since='0.2'/>\n\
        </value-type>\n\
    </typesystem>\n";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode,
                                                                true, QLatin1String("0.1")));
    QVERIFY(!builder.isNull());
    AbstractMetaClassList classes = builder->classes();
    QCOMPARE(classes.size(), 1);
    QCOMPARE(classes[0]->enums().size(), 1);
}

void TestEnum::testAnonymousEnum()
{
    const char* cppCode ="\
    enum { Global0, Global1 };\n\
    struct A {\n\
        enum { A0, A1 };\n\
        enum { isThis = true, isThat = false };\n\
    };\n";
    const char* xmlCode = "\
    <typesystem package=\"Foo\">\n\
        <!-- Uses the first value of the enum to identify it. -->\n\
        <enum-type identified-by-value='Global0'/>\n\
        <value-type name='A'>\n\
            <!-- Uses the second value of the enum to identify it. -->\n\
            <enum-type identified-by-value='A1'/>\n\
            <enum-type identified-by-value='isThis'/>\n\
        </value-type>\n\
    </typesystem>\n";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(!builder.isNull());

    AbstractMetaEnumList globalEnums = builder->globalEnums();
    QCOMPARE(globalEnums.size(), 1);
    QCOMPARE(globalEnums.constFirst().typeEntry()->qualifiedCppName(),
             u"Global0");
    QVERIFY(globalEnums.constFirst().isAnonymous());

    AbstractMetaClassList classes = builder->classes();
    QCOMPARE(classes.size(), 1);
    QCOMPARE(classes[0]->enums().size(), 2);

    auto anonEnumA1 = classes[0]->findEnum(QLatin1String("A1"));
    QVERIFY(anonEnumA1.has_value());
    QVERIFY(anonEnumA1->isAnonymous());
    QCOMPARE(anonEnumA1->typeEntry()->qualifiedCppName(), u"A::A1");

    AbstractMetaEnumValue enumValueA0 = anonEnumA1->values().constFirst();
    QCOMPARE(enumValueA0.name(), u"A0");
    QCOMPARE(enumValueA0.value().value(), 0);
    QCOMPARE(enumValueA0.stringValue(), QString());

    AbstractMetaEnumValue enumValueA1 = anonEnumA1->values().constLast();
    QCOMPARE(enumValueA1.name(), u"A1");
    QCOMPARE(enumValueA1.value().value(), 1);
    QCOMPARE(enumValueA1.stringValue(), QString());

    auto anonEnumIsThis = classes[0]->findEnum(QLatin1String("isThis"));
    QVERIFY(anonEnumIsThis.has_value());
    QVERIFY(anonEnumIsThis->isAnonymous());
    QCOMPARE(anonEnumIsThis->typeEntry()->qualifiedCppName(), u"A::isThis");

    AbstractMetaEnumValue enumValueIsThis = anonEnumIsThis->values().constFirst();
    QCOMPARE(enumValueIsThis.name(), u"isThis");
    QCOMPARE(enumValueIsThis.value().value(), static_cast<int>(true));
    QCOMPARE(enumValueIsThis.stringValue(), u"true");

    AbstractMetaEnumValue enumValueIsThat = anonEnumIsThis->values().constLast();
    QCOMPARE(enumValueIsThat.name(), u"isThat");
    QCOMPARE(enumValueIsThat.value().value(), static_cast<int>(false));
    QCOMPARE(enumValueIsThat.stringValue(), u"false");
}

void TestEnum::testGlobalEnums()
{
    const char* cppCode ="\
    enum EnumA { A0, A1 };\n\
    enum EnumB { B0 = 2, B1 = 0x4 };\n";
    const char* xmlCode = "\
    <typesystem package=\"Foo\">\n\
        <enum-type name='EnumA'/>\n\
        <enum-type name='EnumB'/>\n\
    </typesystem>\n";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(!builder.isNull());

    AbstractMetaEnumList globalEnums = builder->globalEnums();
    QCOMPARE(globalEnums.size(), 2);

    AbstractMetaEnum enumA = globalEnums.constFirst();
    QCOMPARE(enumA.typeEntry()->qualifiedCppName(), u"EnumA");

    AbstractMetaEnumValue enumValueA0 = enumA.values().constFirst();
    QCOMPARE(enumValueA0.name(), u"A0");
    QCOMPARE(enumValueA0.value().value(), 0);
    QCOMPARE(enumValueA0.stringValue(), QString());

    AbstractMetaEnumValue enumValueA1 = enumA.values().constLast();
    QCOMPARE(enumValueA1.name(), u"A1");
    QCOMPARE(enumValueA1.value().value(), 1);
    QCOMPARE(enumValueA1.stringValue(), QString());

    AbstractMetaEnum enumB = globalEnums.constLast();
    QCOMPARE(enumB.typeEntry()->qualifiedCppName(), u"EnumB");

    AbstractMetaEnumValue enumValueB0 = enumB.values().constFirst();
    QCOMPARE(enumValueB0.name(), u"B0");
    QCOMPARE(enumValueB0.value().value(), 2);
    QCOMPARE(enumValueB0.stringValue(), u"2");

    AbstractMetaEnumValue enumValueB1 = enumB.values().constLast();
    QCOMPARE(enumValueB1.name(), u"B1");
    QCOMPARE(enumValueB1.value().value(), 4);
    QCOMPARE(enumValueB1.stringValue(), u"0x4");
}

void TestEnum::testEnumValueFromNeighbourEnum()
{
    const char* cppCode ="\
    namespace A {\n\
        enum EnumA { ValueA0, ValueA1 };\n\
        enum EnumB { ValueB0 = A::ValueA1, ValueB1 = ValueA0 };\n\
    };\n";
    const char* xmlCode = "\
    <typesystem package=\"Foo\">\n\
        <namespace-type name='A'>\n\
            <enum-type name='EnumA'/>\n\
            <enum-type name='EnumB'/>\n\
        </namespace-type>\n\
    </typesystem>\n";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(!builder.isNull());

    AbstractMetaClassList classes = builder->classes();
    QCOMPARE(classes.size(), 1);
    QCOMPARE(classes[0]->enums().size(), 2);

    auto enumA = classes[0]->findEnum(QLatin1String("EnumA"));
    QVERIFY(enumA.has_value());
    QCOMPARE(enumA->typeEntry()->qualifiedCppName(), u"A::EnumA");

    AbstractMetaEnumValue enumValueA0 = enumA->values().constFirst();
    QCOMPARE(enumValueA0.name(), u"ValueA0");
    QCOMPARE(enumValueA0.value().value(), 0);
    QCOMPARE(enumValueA0.stringValue(), QString());

    AbstractMetaEnumValue enumValueA1 = enumA->values().constLast();
    QCOMPARE(enumValueA1.name(), u"ValueA1");
    QCOMPARE(enumValueA1.value().value(), 1);
    QCOMPARE(enumValueA1.stringValue(), QString());

    auto enumB = classes[0]->findEnum(QLatin1String("EnumB"));
    QVERIFY(enumB.has_value());
    QCOMPARE(enumB->typeEntry()->qualifiedCppName(), u"A::EnumB");

    AbstractMetaEnumValue enumValueB0 = enumB->values().constFirst();
    QCOMPARE(enumValueB0.name(), u"ValueB0");
    QCOMPARE(enumValueB0.value().value(), 1);
    QCOMPARE(enumValueB0.stringValue(), u"A::ValueA1");

    AbstractMetaEnumValue enumValueB1 = enumB->values().constLast();
    QCOMPARE(enumValueB1.name(), u"ValueB1");
    QCOMPARE(enumValueB1.value().value(), 0);
    QCOMPARE(enumValueB1.stringValue(), u"ValueA0");
}

void TestEnum::testEnumValueFromExpression()
{
    const char* cppCode ="\
    struct A {\n\
        enum EnumA : unsigned {\n\
            ValueA0 = 3u,\n\
            ValueA1 = ~3u,\n\
            ValueA2 = 0xffffffff,\n\
            ValueA3 = 0xf0,\n\
            ValueA4 = 8 |ValueA3,\n\
            ValueA5 = ValueA3|32,\n\
            ValueA6 = ValueA3 >> 1,\n\
            ValueA7 = ValueA3 << 1\n\
        };\n\
        enum EnumB : int {\n\
            ValueB0 = ~3,\n\
        };\n\
    };\n";
    const char* xmlCode = "\
    <typesystem package=\"Foo\">\n\
        <value-type name='A'>\n\
            <enum-type name='EnumA'/>\n\
            <enum-type name='EnumB'/>\n\
        </value-type>\n\
    </typesystem>\n";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(!builder.isNull());

    AbstractMetaClass *classA = AbstractMetaClass::findClass(builder->classes(), QLatin1String("A"));
    QVERIFY(classA);

    auto enumA = classA->findEnum(QLatin1String("EnumA"));
    QVERIFY(enumA.has_value());
    QVERIFY(!enumA->isSigned());
    QCOMPARE(enumA->typeEntry()->qualifiedCppName(), u"A::EnumA");

    AbstractMetaEnumValue valueA0 = enumA->values().at(0);
    QCOMPARE(valueA0.name(), u"ValueA0");
    QCOMPARE(valueA0.stringValue(), u"3u");
    QCOMPARE(valueA0.value().unsignedValue(), 3u);

    AbstractMetaEnumValue valueA1 = enumA->values().at(1);
    QCOMPARE(valueA1.name(), u"ValueA1");
    QCOMPARE(valueA1.stringValue(), u"~3u");
    QCOMPARE(valueA1.value().unsignedValue(), ~3u);

    AbstractMetaEnumValue valueA2 = enumA->values().at(2);
    QCOMPARE(valueA2.name(), u"ValueA2");
    QCOMPARE(valueA2.stringValue(), u"0xffffffff");
    QCOMPARE(valueA2.value().unsignedValue(), 0xffffffffu);

    AbstractMetaEnumValue valueA3 = enumA->values().at(3);
    QCOMPARE(valueA3.name(), u"ValueA3");
    QCOMPARE(valueA3.stringValue(), u"0xf0");
    QCOMPARE(valueA3.value().unsignedValue(), 0xf0u);

    AbstractMetaEnumValue valueA4 = enumA->values().at(4);
    QCOMPARE(valueA4.name(), u"ValueA4");
    QCOMPARE(valueA4.stringValue(), u"8 |ValueA3");
    QCOMPARE(valueA4.value().unsignedValue(), 8|0xf0u);

    AbstractMetaEnumValue valueA5 = enumA->values().at(5);
    QCOMPARE(valueA5.name(), u"ValueA5");
    QCOMPARE(valueA5.stringValue(), u"ValueA3|32");
    QCOMPARE(valueA5.value().unsignedValue(), 0xf0u|32);

    AbstractMetaEnumValue valueA6 = enumA->values().at(6);
    QCOMPARE(valueA6.name(), u"ValueA6");
    QCOMPARE(valueA6.stringValue(), u"ValueA3 >> 1");
    QCOMPARE(valueA6.value().unsignedValue(), 0xf0u >> 1);

    AbstractMetaEnumValue valueA7 = enumA->values().at(7);
    QCOMPARE(valueA7.name(), u"ValueA7");
    QCOMPARE(valueA7.stringValue(), u"ValueA3 << 1");
    QCOMPARE(valueA7.value().unsignedValue(), 0xf0u << 1);

   const auto enumB = classA->findEnum(QLatin1String("EnumB"));
   QVERIFY(enumB.has_value());
   QVERIFY(enumB->isSigned());
   QCOMPARE(enumB->typeEntry()->qualifiedCppName(), u"A::EnumB");
   QCOMPARE(enumB->values().size(), 1);
   const AbstractMetaEnumValue valueB0 = enumB->values().at(0);
   QCOMPARE(valueB0.name(), u"ValueB0");
   QCOMPARE(valueB0.stringValue(), u"~3");
   QCOMPARE(valueB0.value().value(), ~3);
}

void TestEnum::testPrivateEnum()
{
    const char* cppCode ="\
    class A {\n\
    private:\n\
        enum PrivateEnum { Priv0 = 0x0f, Priv1 = 0xf0 };\n\
    public:\n\
        enum PublicEnum { Pub0 = Priv0, Pub1 = A::Priv1 };\n\
    };\n";
    const char* xmlCode = "\
    <typesystem package=\"Foo\">\n\
        <value-type name='A'>\n\
            <enum-type name='PublicEnum'/>\n\
        </value-type>\n\
    </typesystem>\n";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(!builder.isNull());

    AbstractMetaClass *classA = AbstractMetaClass::findClass(builder->classes(), QLatin1String("A"));
    QVERIFY(classA);
    QCOMPARE(classA->enums().size(), 2);

    auto privateEnum = classA->findEnum(QLatin1String("PrivateEnum"));
    QVERIFY(privateEnum.has_value());
    QVERIFY(privateEnum->isPrivate());
    QCOMPARE(privateEnum->typeEntry()->qualifiedCppName(), u"A::PrivateEnum");

    auto publicEnum = classA->findEnum(QLatin1String("PublicEnum"));
    QVERIFY(publicEnum.has_value());
    QCOMPARE(publicEnum->typeEntry()->qualifiedCppName(), u"A::PublicEnum");

    AbstractMetaEnumValue pub0 = publicEnum->values().constFirst();
    QCOMPARE(pub0.name(), u"Pub0");
    QCOMPARE(pub0.value().value(), 0x0f);
    QCOMPARE(pub0.stringValue(), u"Priv0");

    AbstractMetaEnumValue pub1 = publicEnum->values().constLast();
    QCOMPARE(pub1.name(), u"Pub1");
    QCOMPARE(pub1.value().value(), 0xf0);
    QCOMPARE(pub1.stringValue(), u"A::Priv1");
}

void TestEnum::testTypedefEnum()
{
    const char* cppCode ="\
    typedef enum EnumA {\n\
        A0,\n\
        A1,\n\
    } EnumA;\n";
    const char* xmlCode = "\
    <typesystem package=\"Foo\">\n\
        <enum-type name='EnumA'/>\n\
    </typesystem>\n";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(!builder.isNull());

    AbstractMetaEnumList globalEnums = builder->globalEnums();
    QCOMPARE(globalEnums.size(), 1);

    AbstractMetaEnum enumA = globalEnums.constFirst();
    QCOMPARE(enumA.typeEntry()->qualifiedCppName(), u"EnumA");

    AbstractMetaEnumValue enumValueA0 = enumA.values().constFirst();
    QCOMPARE(enumValueA0.name(), u"A0");
    QCOMPARE(enumValueA0.value().value(), 0);
    QCOMPARE(enumValueA0.stringValue(), u"");

    AbstractMetaEnumValue enumValueA1 = enumA.values().constLast();
    QCOMPARE(enumValueA1.name(), u"A1");
    QCOMPARE(enumValueA1.value().value(), 1);
    QCOMPARE(enumValueA1.stringValue(), QString());
}

// Helper classes and functions for testing enum default value fixing.
// Put the AbstractMetaBuilder into test fixture struct to avoid having
// to re-parse for each data row.

struct EnumDefaultValuesFixture
{
    QSharedPointer<AbstractMetaBuilder> builder;

    AbstractMetaType globalEnum;
    AbstractMetaType testEnum;
    AbstractMetaType testOptions;
};

Q_DECLARE_METATYPE(EnumDefaultValuesFixture)
Q_DECLARE_METATYPE(AbstractMetaType)

static int populateDefaultValuesFixture(EnumDefaultValuesFixture *fixture)
{
    static const char cppCode[] =R"(
enum GlobalEnum { GE1, GE2 };
namespace Test1
{
namespace Test2
{
   enum Enum1 { E1, E2 };
   enum Option { O1, O2 };
} // namespace Test2
} // namespace Test1
)";
    static const char xmlCode[] = R"(
<typesystem package="Foo">
    <enum-type name='GlobalEnum'/>
    <namespace-type name='Test1'>
        <namespace-type name='Test2'>
            <enum-type name='Enum1'/>
            <enum-type name='Option' flags='Options'/>
        </namespace-type>
    </namespace-type>
</typesystem>
)";

    fixture->builder.reset(TestUtil::parse(cppCode, xmlCode, false));
    if (fixture->builder.isNull())
        return -1;

    const auto globalEnums = fixture->builder->globalEnums();
    if (globalEnums.size() != 1)
        return -2;

    fixture->globalEnum = AbstractMetaType(globalEnums.constFirst().typeEntry());
    fixture->globalEnum.decideUsagePattern();

    const AbstractMetaClass *testNamespace = nullptr;
    for (auto *c : fixture->builder->classes()) {
        if (c->name() == u"Test2") {
            testNamespace = c;
            break;
        }
    }
    if (!testNamespace)
        return -3;

    const auto namespaceEnums = testNamespace->enums();
    if (namespaceEnums.size() != 2)
        return -4;
    QList<const EnumTypeEntry *> enumTypeEntries{
        static_cast<const EnumTypeEntry *>(namespaceEnums.at(0).typeEntry()),
        static_cast<const EnumTypeEntry *>(namespaceEnums.at(1).typeEntry())};
    if (enumTypeEntries.constFirst()->flags())
        std::swap(enumTypeEntries[0], enumTypeEntries[1]);
    fixture->testEnum = AbstractMetaType(enumTypeEntries.at(0));
    fixture->testEnum.decideUsagePattern();
    fixture->testOptions = AbstractMetaType(enumTypeEntries.at(1)->flags());
    fixture->testOptions.decideUsagePattern();
    return 0;
}

void TestEnum::testEnumDefaultValues_data()
{
    EnumDefaultValuesFixture fixture;
    const int setupOk = populateDefaultValuesFixture(&fixture);

    QTest::addColumn<EnumDefaultValuesFixture>("fixture");
    QTest::addColumn<int>("setupOk"); // To verify setup
    QTest::addColumn<AbstractMetaType>("metaType"); // Type and parameters for fixup
    QTest::addColumn<QString>("input");
    QTest::addColumn<QString>("expected");

    // Global should just remain unmodified
    QTest::newRow("global") << fixture << setupOk
        << fixture.globalEnum << "GE1" << "GE1";
    QTest::newRow("global-int") << fixture << setupOk
        << fixture.globalEnum << "42" << "42";
    QTest::newRow("global-hex-int") << fixture << setupOk
        << fixture.globalEnum << "0x10" << "0x10";
    QTest::newRow("global-int-cast") << fixture << setupOk
        << fixture.globalEnum << "GlobalEnum(-1)" << "GlobalEnum(-1)";

    // Namespaced enum as number should remain unmodified
    QTest::newRow("namespace-enum-int") << fixture << setupOk
        << fixture.testEnum << "42" << "42";
    QTest::newRow("namespace-enum-hex-int") << fixture << setupOk
        << fixture.testEnum << "0x10" << "0x10";
    // Partial qualification of namespaced enum
    QTest::newRow("namespace-enum-qualified") << fixture << setupOk
        << fixture.testEnum << "Enum1::E1" << "Test1::Test2::Enum1::E1";
    // Unqualified namespaced enums
    QTest::newRow("namespace-enum-unqualified") << fixture << setupOk
        << fixture.testEnum << "E1" << "Test1::Test2::Enum1::E1";
    // Namespaced enums cast from int should be qualified by scope
    QTest::newRow("namespace-enum-int-cast") << fixture << setupOk
        << fixture.testEnum << "Enum1(-1)" << "Test1::Test2::Enum1(-1)";

    // Namespaced option as number should remain unmodified
    QTest::newRow("namespace-option-int") << fixture << setupOk
        << fixture.testOptions << "0x10" << "0x10";
    QTest::newRow("namespace-option-expression") << fixture << setupOk
        << fixture.testOptions << "0x10 | 0x20" << "0x10 | 0x20";
    QTest::newRow("namespace-option-expression1") << fixture << setupOk
        << fixture.testOptions << "0x10 | Test1::Test2::Option::O1"
        << "0x10 | Test1::Test2::Option::O1";
    QTest::newRow("namespace-option-expression2") << fixture << setupOk
        << fixture.testOptions << "0x10 | O1" << "0x10 | Test1::Test2::Option::O1";
    // Complicated expressions - should remain unmodified
    QTest::newRow("namespace-option-expression-paren") << fixture << setupOk
        << fixture.testOptions << "0x10 | (0x20 | 0x40 | O1)"
        << "0x10 | (0x20 | 0x40 | O1)";

    // Option: Cast Enum from int should be qualified
    QTest::newRow("namespace-option-int-cast") << fixture << setupOk
        << fixture.testOptions << "Option(0x10)" << "Test1::Test2::Option(0x10)";
    // Option: Cast Flags from int should be qualified
    QTest::newRow("namespace-options-int-cast") << fixture << setupOk
        << fixture.testOptions << "Options(0x10 | 0x20)" << "Test1::Test2::Options(0x10 | 0x20)";
    QTest::newRow("namespace-option-cast-expression1") << fixture << setupOk
        << fixture.testOptions << "Test1::Test2::Options(0x10 | Test1::Test2::Option::O1)"
        << "Test1::Test2::Options(0x10 | Test1::Test2::Option::O1)";
    QTest::newRow("namespace-option-cast-expression2") << fixture << setupOk
        << fixture.testOptions << "Options(0x10 | O1)"
        << "Test1::Test2::Options(0x10 | Test1::Test2::Option::O1)";
}

void TestEnum::testEnumDefaultValues()
{
    QFETCH(EnumDefaultValuesFixture, fixture);
    QFETCH(int, setupOk);
    QFETCH(AbstractMetaType, metaType);
    QFETCH(QString, input);
    QFETCH(QString, expected);
    QCOMPARE(setupOk, 0);
    const QString actual = fixture.builder->fixEnumDefault(metaType,  input);
    QCOMPARE(actual, expected);
}

QTEST_APPLESS_MAIN(TestEnum)
