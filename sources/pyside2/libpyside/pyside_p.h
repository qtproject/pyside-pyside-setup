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

#ifndef PYSIDE_P_H
#define PYSIDE_P_H

#include <pysidemacros.h>

#include <dynamicqmetaobject.h>

struct SbkObjectType;

namespace PySide
{

// Struct associated with QObject's via Shiboken::Object::getTypeUserData()
struct TypeUserData
{
    explicit TypeUserData(PyTypeObject* type,  const QMetaObject* metaobject, std::size_t size) :
        mo(type, metaobject), cppObjSize(size) {}

    MetaObjectBuilder mo;
    std::size_t cppObjSize;
};

TypeUserData *retrieveTypeUserData(SbkObjectType *sbkTypeObj);
TypeUserData *retrieveTypeUserData(PyTypeObject *pyTypeObj);
TypeUserData *retrieveTypeUserData(PyObject *pyObj);
// For QML
PYSIDE_API const QMetaObject *retrieveMetaObject(PyTypeObject *pyTypeObj);
PYSIDE_API const QMetaObject *retrieveMetaObject(PyObject *pyObj);

} //namespace PySide

#endif // PYSIDE_P_H
