// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDEQOBJECT_P_H
#define PYSIDEQOBJECT_P_H

#include <pysidemacros.h>

#include <QtCore/qtclasshelpermacros.h>

QT_FORWARD_DECLARE_CLASS(QDebug)
QT_FORWARD_DECLARE_CLASS(QObject)

namespace PySide
{

struct debugQObject
{
    debugQObject(const QObject *qobject) : m_qobject(qobject) {}

    const QObject *m_qobject;
};

QDebug operator<<(QDebug debug, const debugQObject &qo);

} //namespace PySide

#endif // PYSIDEQOBJECT_P_H
