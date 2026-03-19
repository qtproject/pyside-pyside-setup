// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "testclangparser.h"
#include <abstractmetabuilder_testutil.h>

#include <clangparser/clangtype.h>
#include <clangparser/triplet.h>

#include <parser/codemodel.h>

#include <QtTest/qtest.h>

using namespace Qt::StringLiterals;

void TestClangParser::testClangTypeParsing_data()
{
    QTest::addColumn<QString>("typeString");
    QTest::addColumn<bool>("expectedSuccess");
    QTest::addColumn<QString>("expectedTypeName");
    QTest::addColumn<QString>("expectedTemplateParameters");

    QTest::newRow("list")
        << QString(u"std::list<int, std::allocator<int>>::value_type"_s)
        << true << QString(u"std::list::value_type"_s) << QString{};

    QTest::newRow("mapData")
        << QString(u"QMapData<std::map<QString, QVariant, std::less<QString>, std::allocator<std::pair<const QString, QVariant>>>>::const_iterator<U, V>"_s)
        << true << QString(u"QMapData::const_iterator"_s) << QString(u"<U, V>"_s);

    QTest::newRow("fail") // unbalanced '>'
        << QString(u"__optional_relop_t<decltype(std::declval<const _Tp &>() > std::declval<const _Up &>())>"_s)
        << false << QString{} <<  QString{};
}

void TestClangParser::testClangTypeParsing()
{
    QFETCH(QString, typeString);
    QFETCH(bool, expectedSuccess);
    QFETCH(QString, expectedTypeName);
    QFETCH(QString, expectedTemplateParameters);

    auto typeNameO = clang::parseTypeName(typeString);
    QCOMPARE(typeNameO.has_value(), expectedSuccess);
    if (typeNameO.has_value()) {
        QCOMPARE(typeNameO->name, expectedTypeName);
        QCOMPARE(typeNameO->templateParameters, expectedTemplateParameters);
    }
}

void TestClangParser::testParseTriplet_data()
{
    QTest::addColumn<QString>("tripletString");
    QTest::addColumn<bool>("expectedOk");
    QTest::addColumn<Architecture>("expectedArchitecture");
    QTest::addColumn<Platform>("expectedPlatform");
    QTest::addColumn<bool>("expectedCompilerPresent");
    QTest::addColumn<Compiler>("expectedCompiler");
    QTest::addColumn<bool>("expectedPlatformVersionPresent");
    QTest::addColumn<QVersionNumber>("expectedPlatformVersion");
    QTest::addColumn<QByteArray>("expectedConverted"); // test back-conversion

    QTest::newRow("Invalid")
        << QString("Invalid"_L1)
        << false << Architecture::X64 << Platform::Linux << false << Compiler::Gpp
        << false << QVersionNumber{} << QByteArray{};

    QTest::newRow("Linux")
        << QString("x86_64-unknown-linux-gnu"_L1)
        << true << Architecture::X64 << Platform::Linux << false << Compiler::Gpp
        << false << QVersionNumber{}
        << "x86_64-unknown-linux-gnu"_ba;

    QTest::newRow("Poky Linux")
        << QString("aarch64-poky-linux"_L1)
        << true << Architecture::Arm64 << Platform::Linux << false << Compiler::Gpp
        << false << QVersionNumber{}
        << "arm64-unknown-linux"_ba;

    QTest::newRow("WindowsArm")
        << QString("aarch64-pc-windows-msvc19.39.0"_L1)
        << true << Architecture::Arm64 << Platform::Windows << true << Compiler::Msvc
        << false << QVersionNumber{}
        << "arm64-pc-windows-msvc"_ba;

    QTest::newRow("Apple")
        << QString("arm64-apple-macosx15.0.0"_L1)
        << true << Architecture::Arm64 << Platform::macOS << false << Compiler::Gpp
        << true << QVersionNumber{15, 0, 0}
        << "arm64-apple-macosx15.0.0"_ba;

    QTest::newRow("AndroidArm32")
        << QString("armv7a-none-linux-android5.1"_L1)
        << true << Architecture::Arm32 << Platform::Android << false << Compiler::Gpp
        << true << QVersionNumber{5, 1}
        << "armv7a-unknown-linux-android5.1"_ba;

    QTest::newRow("AndroidArm64")
        << QString("aarch64-none-linux-androideabi27.1"_L1)
        << true << Architecture::Arm64 << Platform::Android << false << Compiler::Gpp
        << true << QVersionNumber{27, 1}
        << "aarch64-unknown-linux-android27.1"_ba;

    QTest::newRow("iOS")
        << QString("arm64-apple-ios"_L1)
        << true << Architecture::Arm64 << Platform::iOS << false << Compiler::Gpp
        << false << QVersionNumber{}
        << "arm64-apple-ios"_ba;
}

void TestClangParser::testParseTriplet()
{
    QFETCH(QString, tripletString);
    QFETCH(bool, expectedOk);
    QFETCH(Architecture, expectedArchitecture);
    QFETCH(Platform, expectedPlatform);
    QFETCH(bool, expectedCompilerPresent);
    QFETCH(Compiler, expectedCompiler);
    QFETCH(bool, expectedPlatformVersionPresent);
    QFETCH(QVersionNumber, expectedPlatformVersion);
    QFETCH(QByteArray, expectedConverted);

    auto tripletO = Triplet::fromString(tripletString);

    QCOMPARE(tripletO.has_value(), expectedOk);
    if (expectedOk) {
        const Triplet &triplet = tripletO.value();
        QCOMPARE(triplet.architecture(), expectedArchitecture);
        QCOMPARE(triplet.platform(), expectedPlatform);
        if (expectedPlatformVersionPresent) {
            QCOMPARE(triplet.platformVersion().isNull(), expectedPlatformVersion.isNull());
            QCOMPARE(triplet.platformVersion(), expectedPlatformVersion);
        }
        if (expectedCompilerPresent)
            QCOMPARE(triplet.compiler(), expectedCompiler);
        QCOMPARE(triplet.toByteArray(), expectedConverted);
    }
}

void TestClangParser::testFunctionPointers()
{
    static const char cppCode[] =R"(
using FunctionType = void(int);
using FunctionPointerType = void(*)(int);
)";

    auto dom = TestUtil::buildDom(cppCode);
    QVERIFY(dom);
    const auto &typeDefs = dom->typeDefs();
    QCOMPARE(typeDefs.size(), 2);
    for (const auto &typeDef : typeDefs) {
        const auto &type = typeDef->type();
        const auto expectedCategory = typeDef->name() == "FunctionType"_L1
                                          ? TypeCategory::Function : TypeCategory::FunctionPointer;
        QCOMPARE(type.arguments().size(), 1);
        QCOMPARE(type.typeCategory(), expectedCategory);
    }
}

QTEST_APPLESS_MAIN(TestClangParser)
