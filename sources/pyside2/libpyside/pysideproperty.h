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

#ifndef PYSIDE_PROPERTY_H
#define PYSIDE_PROPERTY_H

#include <pysidemacros.h>

#include <sbkpython.h>

#include <QtCore/QMetaObject>

extern "C"
{
    extern PYSIDE_API PyTypeObject *PySidePropertyTypeF(void);

    struct PySidePropertyPrivate;
    struct PYSIDE_API PySideProperty
    {
        PyObject_HEAD
        PySidePropertyPrivate* d;
    };
};

namespace PySide { namespace Property {

typedef void (*MetaCallHandler)(PySideProperty*,PyObject*,QMetaObject::Call, void**);

PYSIDE_API bool checkType(PyObject *pyObj);

/**
 * This function call set property function and pass value as arg
 * This function does not check the property object type
 *
 * @param   self The property object
 * @param   source The QObject witch has the property
 * @param   value The value to set in property
 * @return  Return 0 if ok or -1 if this function fail
 **/
PYSIDE_API int setValue(PySideProperty *self, PyObject *source, PyObject *value);

/**
 * This function call get property function
 * This function does not check the property object type
 *
 * @param   self The property object
 * @param   source The QObject witch has the property
 * @return  Return the result of property get function or 0 if this fail
 **/
PYSIDE_API PyObject *getValue(PySideProperty *self, PyObject *source);

/**
 * This function return the notify name used on this property
 *
 * @param   self The property object
 * @return  Return a const char with the notify name used
 **/
PYSIDE_API const char *getNotifyName(PySideProperty *self);


/**
 * This function search in the source object for desired property
 *
 * @param   source The QObject object
 * @param   name The property name
 * @return  Return a new reference to property object
 **/
PYSIDE_API PySideProperty *getObject(PyObject *source, PyObject *name);

PYSIDE_API void setMetaCallHandler(PySideProperty *self, MetaCallHandler handler);

PYSIDE_API void setTypeName(PySideProperty *self, const char *typeName);

PYSIDE_API void setUserData(PySideProperty *self, void *data);
PYSIDE_API void* userData(PySideProperty *self);

} //namespace Property
} //namespace PySide

#endif
