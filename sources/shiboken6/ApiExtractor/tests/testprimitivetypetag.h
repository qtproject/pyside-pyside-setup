// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TESTPRIMITIVETYPETAG_H
#define TESTPRIMITIVETYPETAG_H

#include <QtCore/QObject>

class TestPrimitiveTypeTag : public QObject
{
    Q_OBJECT
    private slots:
        void testPrimitiveTypeDefaultConstructor();
};

#endif
