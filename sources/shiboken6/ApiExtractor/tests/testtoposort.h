// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TESTTOPOSORT_H
#define TESTTOPOSORT_H

#include <QtCore/QObject>

class TestTopoSort : public QObject
{
Q_OBJECT
private slots:
    void testTopoSort_data();
    void testTopoSort();
};

#endif
