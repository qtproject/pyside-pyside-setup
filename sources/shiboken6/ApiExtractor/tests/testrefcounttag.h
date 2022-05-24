// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TESTREFCOUNTTAG_H
#define TESTREFCOUNTTAG_H

#include <QtCore/QObject>

class TestRefCountTag : public QObject
{
    Q_OBJECT
    private slots:
        void testReferenceCountTag();
        void testWithApiVersion();
};

#endif
