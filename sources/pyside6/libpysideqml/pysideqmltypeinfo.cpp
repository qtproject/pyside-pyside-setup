// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#include "pysideqmltypeinfo_p.h"

#include <QtCore/qdebug.h>
#include <QtCore/qhash.h>

#include <sbkpep.h>

#include <algorithm>

namespace PySide::Qml {

using QmlTypeInfoHash = QHash<const PyObject *, QmlTypeInfoPtr>;

Q_GLOBAL_STATIC(QmlTypeInfoHash, qmlTypeInfoHashStatic);

QmlTypeInfoPtr ensureQmlTypeInfo(const PyObject *o)
{
    auto *hash = qmlTypeInfoHashStatic();
    auto it = hash->find(o);
    if (it == hash->end())
        it = hash->insert(o, std::make_shared<QmlTypeInfo>());
    return it.value();
}

void insertQmlTypeInfoAlias(const PyObject *o, const QmlTypeInfoPtr &value)
{
    qmlTypeInfoHashStatic()->insert(o, value);
}

QmlTypeInfoPtr qmlTypeInfo(const PyObject *o)
{
    auto *hash = qmlTypeInfoHashStatic();
    auto it = hash->constFind(o);
    return it != hash->cend() ? it.value() : QmlTypeInfoPtr{};
}

#ifndef QT_NO_DEBUG_STREAM
QDebug operator<<(QDebug d, const QmlTypeInfo &i)
{
    QDebugStateSaver saver(d);
    d.noquote();
    d.nospace();
    d << "QmlTypeInfo(" << i.flags;
    if (i.foreignType)
        d << ", foreignType=" << PepType_GetFullyQualifiedNameStr(i.foreignType);
    if (i.attachedType)
        d << ", attachedType=" << PepType_GetFullyQualifiedNameStr(i.attachedType);
    if (i.extensionType)
        d << ", extensionType=" << PepType_GetFullyQualifiedNameStr(i.extensionType);
    d << ')';
    return d;
}

QDebug operator<<(QDebug d, const QmlExtensionInfo &e)
{
    QDebugStateSaver saver(d);
    d.noquote();
    d.nospace();
    d << "QmlExtensionInfo(";
    if (e.factory  != nullptr && e.metaObject != nullptr)
        d << '"' << e.metaObject->className() << "\", factory="
          << reinterpret_cast<const void *>(e.factory);
    d << ')';
    return d;
}

#endif // QT_NO_DEBUG_STREAM

} // namespace PySide::Qml
