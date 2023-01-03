// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "testremoveoperatormethod.h"
#include "testutil.h"
#include <abstractmetafunction.h>
#include <abstractmetalang.h>
#include <typesystem.h>

#include <qtcompat.h>

#include <QtTest/QTest>

using namespace Qt::StringLiterals;

void TestRemoveOperatorMethod::testRemoveOperatorMethod()
{
    const char cppCode[] = R"(#include <cstdint>

struct Char {};
struct ByteArray {};
struct String {};

struct A {
    A& operator>>(char&);
    A& operator>>(char*);
    A& operator>>(short&);
    A& operator>>(unsigned short&);
    A& operator>>(int&);
    A& operator>>(unsigned int&);
    A& operator>>(int64_t&);
    A& operator>>(uint64_t&);
    A& operator>>(float&);
    A& operator>>(double&);
    A& operator>>(Char&);
    A& operator>>(ByteArray&);
    A& operator>>(String&);
};
)";

    const char xmlCode[] = "\
    <typesystem package='Foo'>\n\
        <primitive-type name='char'/>\n\
        <primitive-type name='short'/>\n\
        <primitive-type name='unsigned short'/>\n\
        <primitive-type name='int'/>\n\
        <primitive-type name='unsigned int'/>\n\
        <primitive-type name='int64_t'/>\n\
        <primitive-type name='uint64_t'/>\n\
        <primitive-type name='float'/>\n\
        <primitive-type name='double'/>\n\
        <primitive-type name='Char'/>\n\
        <primitive-type name='String'/>\n\
        <value-type name='ByteArray'/>\n\
        <object-type name='A'>\n\
            <modify-function signature='operator&gt;&gt;(char&amp;)' remove='all'/>\n\
            <modify-function signature='operator&gt;&gt;(char*)' remove='all'/>\n\
            <modify-function signature='operator&gt;&gt;(short&amp;)' remove='all'/>\n\
            <modify-function signature='operator&gt;&gt;(unsigned short&amp;)' remove='all'/>\n\
            <modify-function signature='operator&gt;&gt;(int&amp;)' remove='all'/>\n\
            <modify-function signature='operator&gt;&gt;(unsigned int&amp;)' remove='all'/>\n\
            <modify-function signature='operator&gt;&gt;(int64_t&amp;)' remove='all'/>\n\
            <modify-function signature='operator&gt;&gt;(uint64_t&amp;)' remove='all'/>\n\
            <modify-function signature='operator&gt;&gt;(float&amp;)' remove='all'/>\n\
            <modify-function signature='operator&gt;&gt;(double&amp;)' remove='all'/>\n\
            <modify-function signature='operator&gt;&gt;(Char&amp;)' remove='all'/>\n\
            <modify-function signature='operator&gt;&gt;(String&amp;)' remove='all'/>\n\
        </object-type>\n\
    </typesystem>\n";
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode, false));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    const auto classA = AbstractMetaClass::findClass(classes, u"A");
    QVERIFY(classA);
    QCOMPARE(classA->functions().size(), 14);
    QStringList removedSignatures;
    removedSignatures.append(u"operator>>(char&)"_s);
    removedSignatures.append(u"operator>>(char*)"_s);
    removedSignatures.append(u"operator>>(short&)"_s);
    removedSignatures.append(u"operator>>(unsigned short&)"_s);
    removedSignatures.append(u"operator>>(int&)"_s);
    removedSignatures.append(u"operator>>(unsigned int&)"_s);
    removedSignatures.append(u"operator>>(int64_t&)"_s);
    removedSignatures.append(u"operator>>(uint64_t&)"_s);
    removedSignatures.append(u"operator>>(float&)"_s);
    removedSignatures.append(u"operator>>(double&)"_s);
    removedSignatures.append(u"operator>>(Char&)"_s);
    removedSignatures.append(u"operator>>(String&)"_s);
    auto notRemoved = classA->functions().size();
    for (const auto &f : classA->functions()) {
        QCOMPARE(f->isModifiedRemoved(), bool(removedSignatures.contains(f->minimalSignature())));
        notRemoved -= int(f->isModifiedRemoved());
    }
    QCOMPARE(notRemoved, 2);
}

QTEST_APPLESS_MAIN(TestRemoveOperatorMethod)

