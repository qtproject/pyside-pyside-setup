// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef DUMMYGENTABLETEST_H
#define DUMMYGENTABLETEST_H

#include <QObject>

class DummyGenerator;

class DummyGenTest : public QObject
{
    Q_OBJECT

private:
    QString workDir;
    QString headerFilePath;
    QString typesystemFilePath;
    QString generatedFilePath;
    QString projectFilePath;

private slots:
    void initTestCase();
    void testCallGenRunnerWithFullPathToDummyGenModule();
    void testCallGenRunnerWithNameOfDummyGenModule();
    void testCallDummyGeneratorExecutable();
    void testProjectFileArgumentsReading();
};

#endif

