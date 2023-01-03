// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "testnestedtypes.h"
#include "testutil.h"
#include <abstractmetafunction.h>
#include <abstractmetalang.h>
#include <abstractmetatype.h>
#include <codesnip.h>
#include <modifications.h>
#include <complextypeentry.h>
#include <primitivetypeentry.h>

#include <qtcompat.h>

#include <QtTest/QTest>

using namespace Qt::StringLiterals;

void TestNestedTypes::testNestedTypesModifications()
{
    const char cppCode[] = "\
    namespace OuterNamespace {\n\
        namespace InnerNamespace {\n\
            struct SomeClass {\n\
                void method() {}\n\
            };\n\
        };\n\
    };\n";
    const char xmlCode[] = "\
    <typesystem package='Foo'>\n\
        <namespace-type name='OuterNamespace'>\n\
            <namespace-type name='InnerNamespace'>\n\
                <inject-code class='native'>custom_code1();</inject-code>\n\
                <add-function signature='method()' return-type='OuterNamespace::InnerNamespace::SomeClass'>\n\
                    <inject-code class='target'>custom_code2();</inject-code>\n\
                </add-function>\n\
                <object-type name='SomeClass' target-lang-name='RenamedSomeClass'>\n\
                    <modify-function signature='method()' remove='all'/>\n\
                </object-type>\n\
            </namespace-type>\n\
        </namespace-type>\n\
    </typesystem>\n";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();

    const auto ons = AbstractMetaClass::findClass(classes, u"OuterNamespace");
    QVERIFY(ons);

    const auto ins = AbstractMetaClass::findClass(classes, u"OuterNamespace::InnerNamespace");
    QVERIFY(ins);
    QCOMPARE(ins->functions().size(), 1);
    QCOMPARE(ins->typeEntry()->codeSnips().size(), 1);
    CodeSnip snip = ins->typeEntry()->codeSnips().constFirst();
    QCOMPARE(snip.code().trimmed(), u"custom_code1();");

    const auto addedFunc = ins->functions().constFirst();
    QVERIFY(addedFunc->isUserAdded());
    QCOMPARE(addedFunc->access(), Access::Public);
    QCOMPARE(addedFunc->functionType(), AbstractMetaFunction::NormalFunction);
    QCOMPARE(addedFunc->type().minimalSignature(),
             u"OuterNamespace::InnerNamespace::SomeClass");

    QCOMPARE(addedFunc->modifications().size(), 1);
    QVERIFY(addedFunc->modifications().constFirst().isCodeInjection());
    snip = addedFunc->modifications().constFirst().snips().constFirst();
    QCOMPARE(snip.code().trimmed(), u"custom_code2();");

    const auto sc =
        AbstractMetaClass::findClass(classes, u"OuterNamespace::InnerNamespace::SomeClass");
    QVERIFY(sc);
    QCOMPARE(sc->functions().size(), 2); // default constructor and removed method
    const auto removedFunc = sc->functions().constLast();
    QVERIFY(removedFunc->isModifiedRemoved());
}


void TestNestedTypes::testDuplicationOfNestedTypes()
{
    const char cppCode[] = "\
    namespace Namespace {\n\
        class SomeClass {};\n\
    };\n";
    const char xmlCode[] = "\
    <typesystem package='Foo'>\n\
        <namespace-type name='Namespace'>\n\
            <value-type name='SomeClass'>\n\
                <add-function signature='createSomeClass(Namespace::SomeClass)'/>\n\
            </value-type>\n\
        </namespace-type>\n\
    </typesystem>\n";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    QCOMPARE(classes.size(), 2);
    const auto nspace = AbstractMetaClass::findClass(classes, u"Namespace");
    QVERIFY(nspace);
    const auto cls1 = AbstractMetaClass::findClass(classes, u"SomeClass");
    QVERIFY(cls1);
    const auto cls2 = AbstractMetaClass::findClass(classes, u"Namespace::SomeClass");
    QVERIFY(cls2);
    QCOMPARE(cls1, cls2);
    QCOMPARE(cls1->name(), u"SomeClass");
    QCOMPARE(cls1->qualifiedCppName(), u"Namespace::SomeClass");

    auto t1 = TypeDatabase::instance()->findType(u"Namespace::SomeClass"_s);
    QVERIFY(t1);
    auto t2 = TypeDatabase::instance()->findType(u"SomeClass"_s);
    QVERIFY(!t2);
}

QTEST_APPLESS_MAIN(TestNestedTypes)
