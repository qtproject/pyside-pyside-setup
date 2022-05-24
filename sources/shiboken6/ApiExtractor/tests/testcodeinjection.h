// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TESTCODEINJECTIONS_H
#define TESTCODEINJECTIONS_H

#include <QtCore/QObject>

class AbstractMetaBuilder;

class TestCodeInjections : public QObject
{
    Q_OBJECT
private slots:
    void testReadFile_data();
    void testReadFile();
    void testInjectWithValidApiVersion();
    void testInjectWithInvalidApiVersion();
    void testTextStream();
    void testTextStreamRst();
};

#endif
