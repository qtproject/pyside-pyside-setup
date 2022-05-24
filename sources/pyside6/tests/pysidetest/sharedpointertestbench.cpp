// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "sharedpointertestbench.h"

#include <QtCore/QObject>
#include <QtCore/QDebug>

SharedPointerTestbench::SharedPointerTestbench() = default;

QSharedPointer<int> SharedPointerTestbench::createSharedPointerInt(int v)
{
    return QSharedPointer<int>(new int(v));
}

void SharedPointerTestbench::printSharedPointerInt(const QSharedPointer<int> &p)
{
    qDebug() << __FUNCTION__ << *p;
}

QSharedPointer<QObject> SharedPointerTestbench::createSharedPointerQObject()
{
    QSharedPointer<QObject> result(new QObject);
    result->setObjectName(u"TestObject"_qs);
    return result;
}

void SharedPointerTestbench::printSharedPointerQObject(const QSharedPointer<QObject> &p)
{
    qDebug() << __FUNCTION__ << p.data();
}
