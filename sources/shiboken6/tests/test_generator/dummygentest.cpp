// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "dummygentest.h"
#include "dummygenerator.h"
#include "dummygentestconfig.h"

#include <QtCore/QProcess>
#include <QtCore/QTemporaryFile>
#include <QtTest/QTest>

#define GENERATED_CONTENTS  "// Generated code for class: Dummy"

void DummyGenTest::initTestCase()
{
    int argc = 0;
    char* argv[] = {NULL};
    QCoreApplication app(argc, argv);
    workDir = QDir::currentPath();

    headerFilePath = workDir + "/test_global.h";
    typesystemFilePath = workDir + "/test_typesystem.xml";
    projectFilePath = workDir + "/dummygentest-project.txt";
    generatedFilePath = QDir::tempPath() + u"/dummy/dummy_generated.txt"_qs;
}

void DummyGenTest::testCallGenRunnerWithFullPathToDummyGenModule()
{
    QStringList args;
    args.append("--generator-set=" DUMMYGENERATOR_BINARY_DIR "/dummy_generator" MODULE_EXTENSION);
    args.append(u"--output-directory="_qs + QDir::tempPath());
    args.append(headerFilePath);
    args.append(typesystemFilePath);
    int result = QProcess::execute("generatorrunner", args);
    QCOMPARE(result, 0);

    QFile generatedFile(generatedFilePath);
    generatedFile.open(QIODevice::ReadOnly);
    QCOMPARE(generatedFile.readAll().trimmed(), QByteArray(GENERATED_CONTENTS).trimmed());
    generatedFile.close();

    QVERIFY(generatedFile.remove());
}

void DummyGenTest::testCallGenRunnerWithNameOfDummyGenModule()
{
    QStringList args;
    args.append("--generator-set=dummy");
    args.append(u"--output-directory="_qs + QDir::tempPath());
    args.append(headerFilePath);
    args.append(typesystemFilePath);
    int result = QProcess::execute("generatorrunner", args);
    QCOMPARE(result, 0);

    QFile generatedFile(generatedFilePath);
    generatedFile.open(QIODevice::ReadOnly);
    QCOMPARE(generatedFile.readAll().trimmed(), QByteArray(GENERATED_CONTENTS).trimmed());
    generatedFile.close();

    QVERIFY(generatedFile.remove());
}

void DummyGenTest::testCallDummyGeneratorExecutable()
{
    QStringList args;
    args.append(u"--output-directory="_qs + QDir::tempPath());
    args.append(headerFilePath);
    args.append(typesystemFilePath);
    int result = QProcess::execute(DUMMYGENERATOR_BINARY, args);
    QCOMPARE(result, 0);

    QFile generatedFile(generatedFilePath);
    generatedFile.open(QIODevice::ReadOnly);
    QCOMPARE(generatedFile.readAll().trimmed(), QByteArray(GENERATED_CONTENTS).trimmed());
    generatedFile.close();

    QVERIFY(generatedFile.remove());
}

void DummyGenTest::testProjectFileArgumentsReading()
{
    QStringList args(u"--project-file="_qs + workDir + u"/dummygentest-project.txt"_qs);
    int result = QProcess::execute("generatorrunner", args);
    QCOMPARE(result, 0);

    QFile logFile(workDir + "/dummygen-args.log");
    logFile.open(QIODevice::ReadOnly);
    QStringList logContents;
    while (!logFile.atEnd())
        logContents << logFile.readLine().trimmed();
    logContents.sort();
    QCOMPARE(logContents[0], QString("api-version = 1.2.3"));
    QCOMPARE(logContents[1], QString("debug = sparse"));
    QVERIFY(logContents[2].startsWith("dump-arguments = "));
    QVERIFY(logContents[2].endsWith("dummygen-args.log"));
    QCOMPARE(logContents[3], QString("generator-set = dummy"));
    QVERIFY(logContents[4].startsWith("header-file = "));
    QVERIFY(logContents[4].endsWith("test_global.h"));
    QCOMPARE(logContents[5],
             QDir::toNativeSeparators(QString("include-paths = /include/path/location1%1/include/path/location2").arg(PATH_SPLITTER)));
    QCOMPARE(logContents[6], QString("no-suppress-warnings"));
    QCOMPARE(logContents[7], QString("output-directory = /tmp/output"));
    QVERIFY(logContents[8].startsWith("project-file = "));
    QVERIFY(logContents[8].endsWith("dummygentest-project.txt"));
    QVERIFY(logContents[9].startsWith("typesystem-file = "));
    QVERIFY(logContents[9].endsWith("test_typesystem.xml"));
    QCOMPARE(logContents[10],
             QDir::toNativeSeparators(QString("typesystem-paths = /typesystem/path/location1%1/typesystem/path/location2").arg(PATH_SPLITTER)));
}

QTEST_APPLESS_MAIN(DummyGenTest)

#include "dummygentest.moc"

