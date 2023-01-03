// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "testconversionruletag.h"
#include "testutil.h"
#include <abstractmetalang.h>
#include <complextypeentry.h>
#include <customconversion.h>
#include <primitivetypeentry.h>
#include <valuetypeentry.h>

#include <qtcompat.h>

#include <QtCore/QFile>
#include <QtCore/QTemporaryFile>
#include <QtTest/QTest>

using namespace Qt::StringLiterals;

void TestConversionRuleTag::testConversionRuleTagWithFile()
{
    // FIXME PYSIDE7 remove
    // temp file used later
    const char conversionData[] = "Hi! I'm a conversion rule.";
    QTemporaryFile file;
    file.open();
    QCOMPARE(file.write(conversionData), qint64(sizeof(conversionData)-1));
    file.close();

    const char cppCode[] = "struct A {};\n";
    QString xmlCode = u"\
    <typesystem package='Foo'>\n\
        <value-type name='A'>\n\
            <conversion-rule class='target' file='"_s + file.fileName() + u"'/>\n\
        </value-type>\n\
    </typesystem>\n"_s;
    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode.toLocal8Bit().data()));
    QVERIFY(builder);
    AbstractMetaClassList classes = builder->classes();
    const auto classA = AbstractMetaClass::findClass(classes, u"A");
    QVERIFY(classA);
    const auto typeEntry = classA->typeEntry();
    QVERIFY(typeEntry->isValue());
    auto vte = std::static_pointer_cast<const ValueTypeEntry>(typeEntry);
    QVERIFY(vte->hasTargetConversionRule());
    QCOMPARE(vte->targetConversionRule(), QLatin1String(conversionData));
}

void TestConversionRuleTag::testConversionRuleTagReplace()
{
    const char cppCode[] = "\
    struct A {\n\
        A();\n\
        A(const char*, int);\n\
    };\n\
    struct B {\n\
        A createA();\n\
    };\n";
    const char xmlCode[] = "\
    <typesystem package='Foo'>\n\
        <primitive-type name='int'/>\n\
        <primitive-type name='char'/>\n\
        <primitive-type name='A'>\n\
            <conversion-rule>\n\
                <native-to-target>\n\
                DoThis();\n\
                return ConvertFromCppToPython(%IN);\n\
                </native-to-target>\n\
                <target-to-native>\n\
                    <add-conversion type='TargetNone' check='%IN == Target_None'>\n\
                    DoThat();\n\
                    DoSomething();\n\
                    %OUT = A();\n\
                    </add-conversion>\n\
                    <add-conversion type='B' check='CheckIfInputObjectIsB(%IN)'>\n\
                    %OUT = %IN.createA();\n\
                    </add-conversion>\n\
                    <add-conversion type='String' check='String_Check(%IN)'>\n\
                    %OUT = new A(String_AsString(%IN), String_GetSize(%IN));\n\
                    </add-conversion>\n\
                </target-to-native>\n\
            </conversion-rule>\n\
        </primitive-type>\n\
        <value-type name='B'/>\n\
    </typesystem>\n";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode));
    QVERIFY(builder);
    auto *typeDb = TypeDatabase::instance();
    auto typeA = typeDb->findPrimitiveType(u"A"_s);
    QVERIFY(typeA);

    QVERIFY(typeA->hasCustomConversion());
    auto conversion = typeA->customConversion();

    QCOMPARE(typeA, conversion->ownerType());
    QCOMPARE(conversion->nativeToTargetConversion().simplified(),
             u"DoThis(); return ConvertFromCppToPython(%IN);");

    QVERIFY(conversion->replaceOriginalTargetToNativeConversions());
    QVERIFY(conversion->hasTargetToNativeConversions());
    QCOMPARE(conversion->targetToNativeConversions().size(), 3);

    QVERIFY(!conversion->targetToNativeConversions().isEmpty());
    auto toNative = conversion->targetToNativeConversions().at(0);
    QCOMPARE(toNative.sourceTypeName(), u"TargetNone");
    QVERIFY(toNative.isCustomType());
    QCOMPARE(toNative.sourceType(), nullptr);
    QCOMPARE(toNative.sourceTypeCheck(), u"%IN == Target_None");
    QCOMPARE(toNative.conversion().simplified(),
             u"DoThat(); DoSomething(); %OUT = A();");

    QVERIFY(conversion->targetToNativeConversions().size() > 1);
    toNative = conversion->targetToNativeConversions().at(1);
    QCOMPARE(toNative.sourceTypeName(), u"B");
    QVERIFY(!toNative.isCustomType());
    auto typeB = typeDb->findType(u"B"_s);
    QVERIFY(typeB);
    QCOMPARE(toNative.sourceType(), typeB);
    QCOMPARE(toNative.sourceTypeCheck(), u"CheckIfInputObjectIsB(%IN)");
    QCOMPARE(toNative.conversion().trimmed(), u"%OUT = %IN.createA();");

    QVERIFY(conversion->targetToNativeConversions().size() > 2);
    toNative = conversion->targetToNativeConversions().at(2);
    QCOMPARE(toNative.sourceTypeName(), u"String");
    QVERIFY(toNative.isCustomType());
    QCOMPARE(toNative.sourceType(), nullptr);
    QCOMPARE(toNative.sourceTypeCheck(), u"String_Check(%IN)");
    QCOMPARE(toNative.conversion().trimmed(),
             u"%OUT = new A(String_AsString(%IN), String_GetSize(%IN));");
}

void TestConversionRuleTag::testConversionRuleTagAdd()
{
    const char cppCode[] = "\
    struct Date {\n\
        Date();\n\
        Date(int, int, int);\n\
    };\n";
    const char xmlCode[] = "\
    <typesystem package='Foo'>\n\
        <primitive-type name='int'/>\n\
        <value-type name='Date'>\n\
            <conversion-rule>\n\
                <target-to-native replace='no'>\n\
                    <add-conversion type='TargetDate' check='TargetDate_Check(%IN)'>\n\
if (!TargetDateTimeAPI) TargetDateTime_IMPORT;\n\
%OUT = new Date(TargetDate_Day(%IN), TargetDate_Month(%IN), TargetDate_Year(%IN));\n\
                    </add-conversion>\n\
                </target-to-native>\n\
            </conversion-rule>\n\
        </value-type>\n\
    </typesystem>\n";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode));
    QVERIFY(builder);
    const auto classA = AbstractMetaClass::findClass(builder->classes(), u"Date");
    QVERIFY(classA);

    QVERIFY(classA->typeEntry()->isValue());
    auto vte = std::static_pointer_cast<const ValueTypeEntry>(classA->typeEntry());
    QVERIFY(vte->hasCustomConversion());
    auto conversion = vte->customConversion();

    QCOMPARE(conversion->nativeToTargetConversion(), QString());

    QVERIFY(!conversion->replaceOriginalTargetToNativeConversions());
    QVERIFY(conversion->hasTargetToNativeConversions());
    QCOMPARE(conversion->targetToNativeConversions().size(), 1);

    QVERIFY(!conversion->targetToNativeConversions().isEmpty());
    const auto &toNative = conversion->targetToNativeConversions().constFirst();
    QCOMPARE(toNative.sourceTypeName(), u"TargetDate");
    QVERIFY(toNative.isCustomType());
    QCOMPARE(toNative.sourceType(), nullptr);
    QCOMPARE(toNative.sourceTypeCheck(), u"TargetDate_Check(%IN)");
    QCOMPARE(toNative.conversion().trimmed(),
             uR"(if (!TargetDateTimeAPI) TargetDateTime_IMPORT;
%OUT = new Date(TargetDate_Day(%IN), TargetDate_Month(%IN), TargetDate_Year(%IN));)");
}

void TestConversionRuleTag::testConversionRuleTagWithInsertTemplate()
{
    const char cppCode[] = "struct A {};";
    const char xmlCode[] = "\
    <typesystem package='Foo'>\n\
        <primitive-type name='int'/>\n\
        <!-- single line -->\n\
        <template name='native_to_target'>return ConvertFromCppToPython(%IN);</template>\n\
        <!-- multi-line -->\n\
        <template name='target_to_native'>\n\
%OUT = %IN.createA();\n\
        </template>\n\
        <primitive-type name='A'>\n\
            <conversion-rule>\n\
                <native-to-target>\n\
                    <insert-template name='native_to_target'/>\n\
                </native-to-target>\n\
                <target-to-native>\n\
                    <add-conversion type='TargetType'>\n\
                        <insert-template name='target_to_native'/>\n\
                    </add-conversion>\n\
                </target-to-native>\n\
            </conversion-rule>\n\
        </primitive-type>\n\
    </typesystem>\n";

    const char nativeToTargetExpected[] =
    "// TEMPLATE - native_to_target - START\n"
    "return ConvertFromCppToPython(%IN);\n"
    "// TEMPLATE - native_to_target - END";

    const char targetToNativeExpected[] =
    "// TEMPLATE - target_to_native - START\n"
    "%OUT = %IN.createA();\n"
    "// TEMPLATE - target_to_native - END";

    QScopedPointer<AbstractMetaBuilder> builder(TestUtil::parse(cppCode, xmlCode));
    QVERIFY(builder);
    auto *typeDb = TypeDatabase::instance();
    auto typeA = typeDb->findPrimitiveType(u"A"_s);
    QVERIFY(typeA);

    QVERIFY(typeA->hasCustomConversion());
    auto conversion = typeA->customConversion();

    QCOMPARE(typeA, conversion->ownerType());
    QCOMPARE(conversion->nativeToTargetConversion().trimmed(),
             QLatin1StringView(nativeToTargetExpected));

    QVERIFY(conversion->hasTargetToNativeConversions());
    QCOMPARE(conversion->targetToNativeConversions().size(), 1);

    QVERIFY(!conversion->targetToNativeConversions().isEmpty());
    const auto &toNative = conversion->targetToNativeConversions().constFirst();
    QCOMPARE(toNative.conversion().trimmed(),
             QLatin1StringView(targetToNativeExpected));
}

QTEST_APPLESS_MAIN(TestConversionRuleTag)
