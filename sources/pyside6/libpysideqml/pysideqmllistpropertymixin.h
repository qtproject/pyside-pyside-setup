// Copyright (C) 2025 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef QMLLISTPROPERTYMIXIN_H
#define QMLLISTPROPERTYMIXIN_H

#include <sbkpython.h>
#include "pysideqmlmacros.h"

#include <QtQml/qqmllist.h>

#include <QtCore/qflags.h>
#include <QtCore/qmetaobject.h>

/// A mixin for PySide properties handling the registration of QQmlListProperty<>
/// in a metaCall() and providing virtuals for the list functionality.
class QmlListPropertyMixin
{
public:
    Q_DISABLE_COPY_MOVE(QmlListPropertyMixin)

    enum class MethodFlag {
        Count      = 0x01,
        At         = 0x02,
        Append     = 0x04,
        Clear      = 0x08,
        Replace    = 0x10,
        RemoveLast = 0x20
    };
    Q_DECLARE_FLAGS(MethodFlags, MethodFlag)

    QmlListPropertyMixin() noexcept;
    virtual ~QmlListPropertyMixin();

    /// Specifies the methods that are actually implemented (required in
    /// addition to overriding the virtuals due to the internal mechanism
    /// based on function pointers).
    MethodFlags methodFlags() const { return m_methodFlags; }
    void setMethodFlags(MethodFlags mf) { m_methodFlags = mf; }
    void setMethodFlag(MethodFlag mf, bool value) { m_methodFlags.setFlag(mf, value); }

    /// Reimplement to return the count.
    virtual qsizetype count(QQmlListProperty<QObject> *propList) const = 0;
    /// Reimplement to return the elemant at \a index.
    virtual QObject *at(QQmlListProperty<QObject> *propList, qsizetype index) const = 0;

    /// Reimplement to append \a item.
    virtual void append(QQmlListProperty<QObject> *propList, QObject *item);
    /// Reimplement to clear the list.
    virtual void clear(QQmlListProperty<QObject> * propList);
    /// Reimplement to replace element \a index by \a value.
    virtual void replace(QQmlListProperty<QObject> *propList, qsizetype index, QObject *value);
    /// Reimplement to remove the last element.
    virtual void removeLast(QQmlListProperty<QObject> *propList);

protected:
    /// Call this from a metaCall() of a property to register the property.
    void handleMetaCall(PyObject *source, QMetaObject::Call call, void **args);

private:
    MethodFlags m_methodFlags;
};

Q_DECLARE_OPERATORS_FOR_FLAGS(QmlListPropertyMixin::MethodFlags)

#endif // QMLLISTPROPERTYMIXIN_H
