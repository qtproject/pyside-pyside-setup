// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "testcontainer.h"
#include <QtTest/QTest>
#include "testutil.h"
#include <abstractmetalang.h>
#include <abstractmetatype.h>
#include <complextypeentry.h>
#include <containertypeentry.h>

void TestContainer::testContainerType()
{
    const char cppCode[] = "\
    namespace std {\n\
    template<class T>\n\
    class list {\n\
        T get(int x) { return 0; }\n\
    };\n\
    }\n\
    class A : public std::list<int> {\n\
    };\n";
    const char xmlCode[] = "\
    <typesystem package='Foo'>\n\
        <namespace-type name='std' generate='no' />\n\
        <container-type name='std::list' type='list' />\n\
        <object-type name='A'/>\n\
    </typesystem>\n";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, true));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    QCOMPARE(classes.size(), 2);
    //search for class A
    const auto classA = AbstractMetaClass::findClass(classes, u"A");
    QVERIFY(classA);
    auto baseContainer = classA->typeEntry()->baseContainerType();
    QVERIFY(baseContainer);
    QCOMPARE(reinterpret_cast<const ContainerTypeEntry*>(baseContainer.get())->containerKind(),
             ContainerTypeEntry::ListContainer);
}

void TestContainer::testListOfValueType()
{
    const char cppCode[] = "\
    namespace std {\n\
    template<class T>\n\
    class list {\n\
        T get(int x) { return 0; }\n\
    };\n\
    }\n\
    class ValueType {};\n\
    class A : public std::list<ValueType> {\n\
    };\n";
    const char xmlCode[] = "\
    <typesystem package='Foo'>\n\
        <namespace-type name='std' generate='no'/>\n\
        <container-type name='std::list' type='list'/>\n\
        <value-type name='ValueType'/>\n\
        <value-type name='A'/>\n\
    </typesystem>\n";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, true));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    QCOMPARE(classes.size(), 3);

    const auto classA = AbstractMetaClass::findClass(classes, u"A");
    QVERIFY(classA);
    QCOMPARE(classA->templateBaseClassInstantiations().size(), 1);
    const AbstractMetaType templateInstanceType =
        classA->templateBaseClassInstantiations().constFirst();

    QCOMPARE(templateInstanceType.indirections(), 0);
    QVERIFY(!templateInstanceType.typeEntry()->isObject());
    QVERIFY(templateInstanceType.typeEntry()->isValue());
    QCOMPARE(templateInstanceType.referenceType(), NoReference);
    QVERIFY(!templateInstanceType.isObject());
    QVERIFY(!templateInstanceType.isValuePointer());
    QVERIFY(templateInstanceType.isValue());
}

QTEST_APPLESS_MAIN(TestContainer)

