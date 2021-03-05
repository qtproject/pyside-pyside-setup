/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:COMM$
**
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** $QT_END_LICENSE$
**
****************************************************************************/

#ifndef DYNAMICQMETAOBJECT_H
#define DYNAMICQMETAOBJECT_H

#include <sbkpython.h>

#include <QtCore/QMetaObject>
#include <QtCore/QMetaMethod>

class MetaObjectBuilderPrivate;

namespace PySide
{

class MetaObjectBuilder
{
    Q_DISABLE_COPY(MetaObjectBuilder)
public:
    MetaObjectBuilder(const char *className, const QMetaObject *metaObject);

    MetaObjectBuilder(PyTypeObject *type, const QMetaObject *metaObject);
    ~MetaObjectBuilder();

    int indexOfMethod(QMetaMethod::MethodType mtype, const QByteArray &signature) const;
    int indexOfProperty(const QByteArray &name) const;
    int addSlot(const char *signature);
    int addSlot(const char *signature, const char *type);
    int addSignal(const char *signature);
    void removeMethod(QMetaMethod::MethodType mtype, int index);
    int addProperty(const char *property, PyObject *data);
    void addInfo(const char *key, const char *value);
    void addInfo(const QMap<QByteArray, QByteArray> &info);
    void addEnumerator(const char *name,
                       bool flag,
                       bool scoped,
                       const QVector<QPair<QByteArray, int> > &entries);
    void removeProperty(int index);

    const QMetaObject *update();

private:
    MetaObjectBuilderPrivate *m_d;
};

}
#endif
