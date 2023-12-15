// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "testremovefield.h"
#include <QtTest/QTest>
#include "testutil.h"
#include <abstractmetaargument.h>
#include <abstractmetafield.h>
#include <abstractmetafunction.h>
#include <abstractmetatype.h>
#include <abstractmetalang.h>
#include <typesystem.h>

using namespace Qt::StringLiterals;

void TestRemoveField::testRemoveField()
{
    const char cppCode[] = "\
    struct A {\n\
        int fieldA;\n\
        int fieldB;\n\
    };\n";
    const char xmlCode[] = "\
    <typesystem package=\"Foo\">\n\
        <primitive-type name='int'/>\n\
        <value-type name='A'>\n\
            <modify-field name='fieldB' remove='all'/>\n\
        </value-type>\n\
    </typesystem>\n";
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    const auto classA = AbstractMetaClass::findClass(classes, "A");
    QVERIFY(classA);
    QCOMPARE(classA->fields().size(), 1);
    const AbstractMetaField &fieldA = classA->fields().constFirst();
    QCOMPARE(fieldA.name(), u"fieldA");
}

// Verify that 'static constexpr' fields are seen as static/const and
// appear fully qualified for function parameter default values.
void TestRemoveField::testConstExprField()
{
    const char cppCode[] = R"(
struct A {
    static constexpr int constExprField = 44;

    void f(int iParam=constExprField);
};
)";

    const char xmlCode[] = R"(
<typesystem package="Foo">
    <value-type name='A'/>
</typesystem>
)";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    const auto classA = AbstractMetaClass::findClass(classes, "A");
    QVERIFY(classA);
    const auto &fields = classA->fields();
    QCOMPARE(fields.size(), 1);
    QVERIFY(fields.constFirst().isStatic());
    QVERIFY(fields.constFirst().type().isConstant());
    const auto function = classA->findFunction("f"_L1);
    QVERIFY(function);
    const auto &arguments = function->arguments();
    QCOMPARE(arguments.size(), 1);
    QCOMPARE(arguments.constFirst().defaultValueExpression(), "A::constExprField"_L1);
}

QTEST_APPLESS_MAIN(TestRemoveField)


