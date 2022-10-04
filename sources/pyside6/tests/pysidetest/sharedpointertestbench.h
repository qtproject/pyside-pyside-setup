// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef SHAREDPOINTERTESTBENCH_H
#define SHAREDPOINTERTESTBENCH_H

#include "pysidetest_macros.h"

#include <QtCore/QSharedPointer>

QT_FORWARD_DECLARE_CLASS(QObject)

class PYSIDETEST_API SharedPointerTestbench
{
public:
    SharedPointerTestbench();

    static QSharedPointer<int> createSharedPointerInt(int v);
    static void printSharedPointerInt(const QSharedPointer<int> &p);

    static QSharedPointer<QObject> createSharedPointerQObject();
    static void printSharedPointerQObject(const QSharedPointer<QObject> &p);

    static QSharedPointer<const QObject> createSharedPointerConstQObject();
    static void printSharedPointerConstQObject(const QSharedPointer<const QObject> &p);

};

#endif // SHAREDPOINTERTESTBENCH_H
