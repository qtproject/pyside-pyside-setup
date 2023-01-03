// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "testremovefield.h"
#include <QtTest/QTest>
#include "testutil.h"
#include <abstractmetafield.h>
#include <abstractmetalang.h>
#include <typesystem.h>

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
    const auto classA = AbstractMetaClass::findClass(classes, u"A");
    QVERIFY(classA);
    QCOMPARE(classA->fields().size(), 1);
    const AbstractMetaField &fieldA = classA->fields().constFirst();
    QCOMPARE(fieldA.name(), u"fieldA");
}

QTEST_APPLESS_MAIN(TestRemoveField)


