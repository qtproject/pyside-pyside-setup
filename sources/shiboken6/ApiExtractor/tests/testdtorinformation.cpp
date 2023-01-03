// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "testdtorinformation.h"
#include "abstractmetabuilder.h"
#include <QtTest/QTest>
#include "testutil.h"
#include <abstractmetalang.h>
#include <typesystem.h>

void TestDtorInformation::testDtorIsPrivate()
{
    const char cppCode[] = R"(class Control {
public:
    ~Control() {}
};
class Subject {
private:
    ~Subject() {}
};
)";
    const char xmlCode[] = R"(<typesystem package="Foo">
    <value-type name="Control"/>
    <value-type name="Subject"/>
</typesystem>)";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    QCOMPARE(classes.size(), 2);
    auto klass = AbstractMetaClass::findClass(classes, u"Control");
    QVERIFY(klass);
    QVERIFY(!klass->hasPrivateDestructor());
    klass = AbstractMetaClass::findClass(classes, u"Subject");
    QVERIFY(klass);
    QVERIFY(klass->hasPrivateDestructor());
}

void TestDtorInformation::testDtorIsProtected()
{
    const char  cppCode[] = R"(class Control {
public:
    ~Control() {}
};
class Subject {
protected:
    ~Subject() {}
};
)";
    const char xmlCode[] = R"(<typesystem package="Foo">
    <value-type name="Control"/>
    <value-type name="Subject"/>
</typesystem>)";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    QCOMPARE(classes.size(), 2);
    auto klass = AbstractMetaClass::findClass(classes, u"Control");
    QVERIFY(klass);
    QVERIFY(!klass->hasProtectedDestructor());
    klass = AbstractMetaClass::findClass(classes, u"Subject");
    QVERIFY(klass);
    QVERIFY(klass->hasProtectedDestructor());
}

void TestDtorInformation::testDtorIsVirtual()
{
    const char cppCode[] = R"(class Control {
public:
    ~Control() {}
};
class Subject {
protected:
    virtual ~Subject() {}
};
)";
    const char xmlCode[] = R"(<typesystem package="Foo">
    <value-type name="Control"/>
    <value-type name="Subject"/>
</typesystem>)";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    QCOMPARE(classes.size(), 2);
    auto klass = AbstractMetaClass::findClass(classes, u"Control");
    QVERIFY(klass);
    QVERIFY(!klass->hasVirtualDestructor());
    klass = AbstractMetaClass::findClass(classes, u"Subject");
    QVERIFY(klass);
    QVERIFY(klass->hasVirtualDestructor());
}

void TestDtorInformation::testDtorFromBaseIsVirtual()
{
    const char cppCode[] = R"CPP(class ControlBase { public: ~ControlBase() {} };
class Control : public ControlBase {};
class SubjectBase { public: virtual ~SubjectBase() {} };
class Subject : public SubjectBase {};
)CPP";
    const char xmlCode[] = R"XML(<typesystem package="Foo"><value-type name="ControlBase"/>
<value-type name="Control"/>"
<value-type name="SubjectBase"/>"
<value-type name="Subject"/>
</typesystem>
)XML";
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    QCOMPARE(classes.size(), 4);

    auto klass = AbstractMetaClass::findClass(classes, u"ControlBase");
    QVERIFY(klass);
    QVERIFY(!klass->hasVirtualDestructor());
    klass = AbstractMetaClass::findClass(classes, u"Control");
    QVERIFY(klass);
    QVERIFY(!klass->hasVirtualDestructor());

    klass = AbstractMetaClass::findClass(classes, u"SubjectBase");
    QVERIFY(klass);
    QVERIFY(klass->hasVirtualDestructor());
    klass = AbstractMetaClass::findClass(classes, u"Subject");
    QVERIFY(klass);
    QVERIFY(klass->hasVirtualDestructor());
}

void TestDtorInformation::testClassWithVirtualDtorIsPolymorphic()
{
    const char cppCode[] = R"(class Control {
public:
    virtual ~Control() {}
};
class Subject {
protected:
    virtual ~Subject() {}
};
)";
    const char xmlCode[] =  R"(<typesystem package="Foo">
    <value-type name="Control"/>
    <value-type name="Subject"/>
</typesystem>)";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    QCOMPARE(classes.size(), 2);
    auto klass = AbstractMetaClass::findClass(classes, u"Control");
    QVERIFY(klass);
    QVERIFY(klass->isPolymorphic());
    klass = AbstractMetaClass::findClass(classes, u"Subject");
    QVERIFY(klass);
    QVERIFY(klass->isPolymorphic());
}

QTEST_APPLESS_MAIN(TestDtorInformation)


