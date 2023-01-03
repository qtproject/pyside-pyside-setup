// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "testinserttemplate.h"
#include <QtTest/QTest>
#include "testutil.h"
#include <abstractmetalang.h>
#include <codesnip.h>
#include <modifications.h>
#include <complextypeentry.h>
#include <typesystemtypeentry.h>

void TestInsertTemplate::testInsertTemplateOnClassInjectCode()
{
    const char cppCode[] = "struct A{};\n";
    const char xmlCode[] = "\
    <typesystem package='Foo'>\n\
        <template name='code_template'>\n\
        code template content\n\
        </template>\n\
        <value-type name='A'>\n\
            <inject-code class='native'>\n\
                <insert-template name='code_template'/>\n\
            </inject-code>\n\
        </value-type>\n\
    </typesystem>\n";
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    QCOMPARE(classes.size(), 1);
    const auto classA = AbstractMetaClass::findClass(classes, u"A");
    QVERIFY(classA);
    QCOMPARE(classA->typeEntry()->codeSnips().size(), 1);
    QString code = classA->typeEntry()->codeSnips().constFirst().code();
    QVERIFY(code.contains(u"code template content"));
}

void TestInsertTemplate::testInsertTemplateOnModuleInjectCode()
{
    const char cppCode[] = "";
    const char xmlCode[] = "\
    <typesystem package='Foo'>\n\
        <template name='code_template'>\n\
        code template content\n\
        </template>\n\
        <inject-code class='native'>\n\
            <insert-template name='code_template'/>\n\
        </inject-code>\n\
    </typesystem>\n";
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    QVERIFY(classes.isEmpty());

    TypeSystemTypeEntryCPtr module = TypeDatabase::instance()->defaultTypeSystemType();
    QVERIFY(module);
    QCOMPARE(module->name(), u"Foo");
    QCOMPARE(module->codeSnips().size(), 1);
    QString code = module->codeSnips().constFirst().code().trimmed();
    QVERIFY(code.contains(u"code template content"));
}

QTEST_APPLESS_MAIN(TestInsertTemplate)
