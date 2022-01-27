/****************************************************************************
**
** Copyright (C) 2022 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:LGPL$
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** GNU Lesser General Public License Usage
** Alternatively, this file may be used under the terms of the GNU Lesser
** General Public License version 3 as published by the Free Software
** Foundation and appearing in the file LICENSE.LGPL3 included in the
** packaging of this file. Please review the following information to
** ensure the GNU Lesser General Public License version 3 requirements
** will be met: https://www.gnu.org/licenses/lgpl-3.0.html.
**
** GNU General Public License Usage
** Alternatively, this file may be used under the terms of the GNU
** General Public License version 2.0 or (at your option) the GNU General
** Public license version 3 or any later version approved by the KDE Free
** Qt Foundation. The licenses are as published by the Free Software
** Foundation and appearing in the file LICENSE.GPL2 and LICENSE.GPL3
** included in the packaging of this file. Please review the following
** information to ensure the GNU General Public License requirements will
** be met: https://www.gnu.org/licenses/gpl-2.0.html and
** https://www.gnu.org/licenses/gpl-3.0.html.
**
** $QT_END_LICENSE$
**
****************************************************************************/

#ifndef PYSIDEQMLTYPEINFO_P_H
#define PYSIDEQMLTYPEINFO_P_H

#include <sbkpython.h>

#include <QtCore/QFlags>
#include <QtCore/QSharedPointer>

#include <string>

QT_FORWARD_DECLARE_CLASS(QDebug)
QT_FORWARD_DECLARE_CLASS(QObject)
QT_FORWARD_DECLARE_STRUCT(QMetaObject)

namespace PySide::Qml {

enum class QmlTypeFlag
{
    Singleton = 0x1,
    Uncreatable = 0x2
};

Q_DECLARE_FLAGS(QmlTypeFlags, QmlTypeFlag)
Q_DECLARE_OPERATORS_FOR_FLAGS(QmlTypeFlags)

// Type information associated with QML type objects
struct QmlTypeInfo
{
    QmlTypeFlags flags;
    std::string noCreationReason;
    PyTypeObject *foreignType = nullptr;
    PyTypeObject *attachedType = nullptr;
    PyTypeObject *extensionType = nullptr;
};

using QmlTypeInfoPtr = QSharedPointer<QmlTypeInfo>;

QmlTypeInfoPtr ensureQmlTypeInfo(const PyObject *o);
void insertQmlTypeInfoAlias(const PyObject *o, const QmlTypeInfoPtr &value);
QmlTypeInfoPtr qmlTypeInfo(const PyObject *o);

// Meta Object and factory function for QmlExtended/QmlAttached
struct QmlExtensionInfo
{
    using Factory = QObject *(*)(QObject *);

    Factory factory;
    const QMetaObject *metaObject;
};

#ifndef QT_NO_DEBUG_STREAM
QDebug operator<<(QDebug d, const QmlTypeInfo &);
QDebug operator<<(QDebug d, const QmlExtensionInfo &);
#endif

} // namespace PySide::Qml

#endif // PYSIDEQMLTYPEINFO_P_H
