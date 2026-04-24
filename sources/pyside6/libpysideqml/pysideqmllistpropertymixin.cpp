// Copyright (C) 2025 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#include "pysideqmllistpropertymixin.h"

#include <pysideqobject.h>

#include <sbkconverter.h>

#include <QtCore/qobject.h>

static qsizetype countHandler(QQmlListProperty<QObject> *propList)
{
    auto *m = reinterpret_cast<QmlListPropertyMixin *>(propList->data);
    return m->count(propList);
}

static QObject *atHandler(QQmlListProperty<QObject> *propList, qsizetype index)
{
    auto *m = reinterpret_cast<QmlListPropertyMixin *>(propList->data);
    return m->at(propList, index);
}

static void appendHandler(QQmlListProperty<QObject> *propList, QObject *item)
{
    auto *m = reinterpret_cast<QmlListPropertyMixin *>(propList->data);
    m->append(propList, item);
}

static void clearHandler(QQmlListProperty<QObject> *propList)
{
    auto *m = reinterpret_cast<QmlListPropertyMixin *>(propList->data);
    m->clear(propList);
}

static void replaceHandler(QQmlListProperty<QObject> *propList, qsizetype index, QObject *value)
{
    auto *m = reinterpret_cast<QmlListPropertyMixin *>(propList->data);
    m->replace(propList, index, value);
}

static void removeLastHandler(QQmlListProperty<QObject> *propList)
{
    auto *m = reinterpret_cast<QmlListPropertyMixin *>(propList->data);
    m->removeLast(propList);
}

QmlListPropertyMixin::QmlListPropertyMixin() noexcept = default;
QmlListPropertyMixin::~QmlListPropertyMixin() = default;

void QmlListPropertyMixin::handleMetaCall(PyObject *source, QMetaObject::Call call, void **args)
{
    if (call != QMetaObject::ReadProperty)
        return;

    QObject *qobj{};
    PyTypeObject *qobjectType = PySide::qObjectType();
    Shiboken::Conversions::pythonToCppPointer(qobjectType, source, &qobj);

    QQmlListProperty<QObject> declProp(
        qobj, this,
        m_methodFlags.testFlag(MethodFlag::Append) ? appendHandler : nullptr,
        m_methodFlags.testFlag(MethodFlag::Count) ? countHandler : nullptr,
        m_methodFlags.testFlag(MethodFlag::At) ? atHandler : nullptr,
        m_methodFlags.testFlag(MethodFlag::Clear) ? clearHandler : nullptr,
        m_methodFlags.testFlag(MethodFlag::Replace) ? replaceHandler : nullptr,
        m_methodFlags.testFlag(MethodFlag::RemoveLast) ? removeLastHandler : nullptr);

    // Copy the data to the memory location requested by the meta call
    void *v = args[0];
    *reinterpret_cast<QQmlListProperty<QObject> *>(v) = declProp;
}

void QmlListPropertyMixin::append(QQmlListProperty<QObject> *, QObject *)
{
}

void QmlListPropertyMixin::clear(QQmlListProperty<QObject> *)
{
}

void QmlListPropertyMixin::replace(QQmlListProperty<QObject> *, qsizetype, QObject *)
{
}

void QmlListPropertyMixin::removeLast(QQmlListProperty<QObject> *)
{
}
