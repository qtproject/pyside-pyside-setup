// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "testreferencetopointer.h"

#include <abstractmetaargument.h>
#include <abstractmetabuilder.h>
#include <abstractmetabuilder_testutil.h>
#include <abstractmetafunction.h>
#include <abstractmetalang.h>
#include <abstractmetatype.h>
#include <typesystem.h>

#include <QtTest/qtest.h>

void TestReferenceToPointer::testReferenceToPointerArgument()
{
    const char cppCode[] = "\
    struct A {};\n\
    struct B {\n\
        void dummy(A*&);\n\
    };\n";
    const char xmlCode[] = "\
    <typesystem package=\"Foo\">\n\
        <object-type name='A'/>\n\
        <object-type name='B'/>\n\
    </typesystem>\n";
    auto builder = TestUtil::parse(cppCode, xmlCode, false);
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    const auto classB = AbstractMetaClass::findClass(classes, "B");
    QVERIFY(classB);
    const auto func = classB->findFunction("dummy");
    QVERIFY(func);
    QCOMPARE(func->arguments().constFirst().type().minimalSignature(), u"A*&");
}

QTEST_APPLESS_MAIN(TestReferenceToPointer)
