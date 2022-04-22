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

#include "testnestedtypes.h"
#include "testutil.h"
#include <abstractmetafunction.h>
#include <abstractmetalang.h>
#include <modifications.h>
#include <typesystem.h>

#include <qtcompat.h>

#include <QtTest/QTest>

using namespace Qt::StringLiterals;

void TestNestedTypes::testNestedTypesModifications()
{
    const char* cppCode ="\
    namespace OuterNamespace {\n\
        namespace InnerNamespace {\n\
            struct SomeClass {\n\
                void method() {}\n\
            };\n\
        };\n\
    };\n";
    const char* xmlCode = "\
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
    QVERIFY(!builder.isNull());
    AbstractMetaClassList classes = builder->classes();

    auto *ons = AbstractMetaClass::findClass(classes, u"OuterNamespace");
    QVERIFY(ons);

    auto *ins = AbstractMetaClass::findClass(classes, u"OuterNamespace::InnerNamespace");
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

    auto *sc = AbstractMetaClass::findClass(classes, u"OuterNamespace::InnerNamespace::SomeClass");
    QVERIFY(ins);
    QCOMPARE(sc->functions().size(), 2); // default constructor and removed method
    const auto removedFunc = sc->functions().constLast();
    QVERIFY(removedFunc->isModifiedRemoved());
}


void TestNestedTypes::testDuplicationOfNestedTypes()
{
    const char* cppCode ="\
    namespace Namespace {\n\
        class SomeClass {};\n\
    };\n";
    const char* xmlCode = "\
    <typesystem package='Foo'>\n\
        <namespace-type name='Namespace'>\n\
            <value-type name='SomeClass'>\n\
                <add-function signature='createSomeClass(Namespace::SomeClass)'/>\n\
            </value-type>\n\
        </namespace-type>\n\
    </typesystem>\n";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(!builder.isNull());
    AbstractMetaClassList classes = builder->classes();
    QCOMPARE(classes.size(), 2);
    auto *nspace = AbstractMetaClass::findClass(classes, u"Namespace");
    QVERIFY(nspace);
    auto *cls1 = AbstractMetaClass::findClass(classes, u"SomeClass");
    QVERIFY(cls1);
    auto *cls2 = AbstractMetaClass::findClass(classes, u"Namespace::SomeClass");
    QVERIFY(cls2);
    QCOMPARE(cls1, cls2);
    QCOMPARE(cls1->name(), u"SomeClass");
    QCOMPARE(cls1->qualifiedCppName(), u"Namespace::SomeClass");

    TypeEntry* t1 = TypeDatabase::instance()->findType(u"Namespace::SomeClass"_s);
    QVERIFY(t1);
    TypeEntry* t2 = TypeDatabase::instance()->findType(u"SomeClass"_s);
    QVERIFY(!t2);
}

QTEST_APPLESS_MAIN(TestNestedTypes)
