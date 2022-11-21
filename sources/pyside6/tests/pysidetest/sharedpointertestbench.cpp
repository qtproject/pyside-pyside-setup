// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "sharedpointertestbench.h"

#include <QtCore/QObject>
#include <QtCore/QDebug>

using namespace Qt::StringLiterals;

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
    result->setObjectName(u"TestObject"_s);
    return result;
}

void SharedPointerTestbench::printSharedPointerQObject(const QSharedPointer<QObject> &p)
{
    qDebug() << __FUNCTION__ << p.data();
}

QSharedPointer<const QObject> SharedPointerTestbench::createSharedPointerConstQObject()
{
    auto *o = new QObject;
    o->setObjectName(u"ConstTestObject"_s);
    QSharedPointer<const QObject> result(o);
    return result;
}

void SharedPointerTestbench::printSharedPointerConstQObject(const QSharedPointer<const QObject> &p)
{
    qDebug() << __FUNCTION__ << p.data();
}
