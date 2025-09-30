// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef DYNAMICQMETAOBJECT_H
#define DYNAMICQMETAOBJECT_H

#include <sbkpython.h>
#include <pysidemacros.h>

#include <QtCore/qmetaobject.h>
#include <QtCore/qmetaobject.h>
#include <QtCore/qvariant.h>

#include <utility>

class MetaObjectBuilderPrivate;

namespace PySide
{

class PYSIDE_API MetaObjectBuilder
{
    Q_DISABLE_COPY_MOVE(MetaObjectBuilder)
public:
    using EnumValue = std::pair<QByteArray, QVariant>; // Int/ULongLong
    using EnumValues = QList<EnumValue>;

    // Plain wrapped Qt types
    explicit MetaObjectBuilder(const QMetaObject *metaObject);
    // Types defined in Python which are parsed
    explicit MetaObjectBuilder(PyTypeObject *type, const QMetaObject *metaObject);
    ~MetaObjectBuilder();

    int indexOfMethod(QMetaMethod::MethodType mtype, const QByteArray &signature) const;
    int indexOfProperty(const QByteArray &name) const;
    int addSlot(const QByteArray &signature);
    int addSlot(const QByteArray &signature, const QByteArray &type);
    int addSignal(const QByteArray &signature);
    void removeMethod(QMetaMethod::MethodType mtype, int index);
    int addProperty(const char *property, PyObject *data);
    void addInfo(const char *key, const char *value);
    void addInfo(const QMap<QByteArray, QByteArray> &info);
    void addEnumerator(const char *name, bool flag,
                       bool scoped, const EnumValues &entries);
    void removeProperty(int index);

    const QMetaObject *update();

    static QString formatMetaObject(const QMetaObject *metaObject);

private:
    MetaObjectBuilderPrivate *m_d;
};

}
#endif
