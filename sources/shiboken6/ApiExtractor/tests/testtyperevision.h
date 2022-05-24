// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TESTTYPEREVISION_H
#define TESTTYPEREVISION_H

#include <QtCore/QObject>

class TestTypeRevision : public QObject
{
    Q_OBJECT

private slots:
    void testRevisionAttr();
    void testVersion_data();
    void testVersion();
};

#endif
