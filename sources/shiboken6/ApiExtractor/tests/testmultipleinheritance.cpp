// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "testmultipleinheritance.h"
#include <QtTest/QTest>
#include "testutil.h"
#include <abstractmetafunction.h>
#include <abstractmetalang.h>
#include <typesystem.h>

void TestMultipleInheritance::testVirtualClass()
{
    const char cppCode[] = "\
    struct A {\n\
        virtual ~A();\n\
        virtual void theBug();\n\
    };\n\
    struct B {\n\
        virtual ~B();\n\
    };\n\
    struct C : A, B {\n\
    };\n\
    struct D : C {\n\
    };\n";
    const char xmlCode[] = "\
    <typesystem package=\"Foo\">\n\
        <object-type name='A' />\n\
        <object-type name='B' />\n\
        <object-type name='C' />\n\
        <object-type name='D' />\n\
    </typesystem>\n";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    QCOMPARE(classes.size(), 4);

    const auto classD = AbstractMetaClass::findClass(classes, u"D");
    bool functionFound = false;
    for (const auto &f : classD->functions()) {
        if (f->name() == u"theBug") {
            functionFound = true;
            break;
        }
    }
    QVERIFY(functionFound);

}

QTEST_APPLESS_MAIN(TestMultipleInheritance)
