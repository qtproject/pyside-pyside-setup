// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef PYSIDE_PROPERTY_H
#define PYSIDE_PROPERTY_H

#include <pysidemacros.h>

#include <sbkpython.h>

class PySidePropertyBase;

extern "C"
{
    extern PYSIDE_API PyTypeObject *PySideProperty_TypeF(void);

    struct PYSIDE_API PySideProperty
    {
        PyObject_HEAD
        PySidePropertyBase* d;
    };
};

namespace PySide::Property {

PYSIDE_API bool checkType(PyObject *pyObj);

/*!
    Calls the setter function of the property \a self on the QObject
    \a source passing \a value as argument.
    This function does not check the property object type.
    Returns 0 on success or -1 on failure.
*/
PYSIDE_API int setValue(PySideProperty *self, PyObject *source, PyObject *value);

/*!
    Calls the getter function of the property \a self on the QObject
    \a source. This function does not check the property object type.
    Returns the result of the getter function or \nullptr on failure.
*/
PYSIDE_API PyObject *getValue(PySideProperty *self, PyObject *source);

/*!
    Returns the notify signal name used by the property \a self.
*/
PYSIDE_API const char *getNotifyName(PySideProperty *self);


/*!
    Searches the QObject \a source for the property named \a name.
    Returns a new reference to the property object.
*/
PYSIDE_API PySideProperty *getObject(PyObject *source, PyObject *name);

PYSIDE_API void setTypeName(PySideProperty *self, const char *typeName);

/*!
    Creates a property from the type name \a typeName, the \a getter,
    the \a setter and the notification signature \a notifySignature,
    optionally passing the private data \a data.
*/
PYSIDE_API PyObject *create(const char *typeName, PyObject *getter,
                            PyObject *setter, PyObject *notifySignature,
                            PySidePropertyBase *data = nullptr);
/*!
    \overload
    Creates a property from the type name \a typeName, the \a getter,
    the optional \a setter and the notification signature \a notifySignature,
    optionally passing the private data \a data.
*/
PYSIDE_API PyObject *create(const char *typeName, PyObject *getter,
                            PyObject *setter = nullptr,
                            const char *notifySignature = nullptr,
                            PySidePropertyBase *data = nullptr);

} //namespace PySide::Property

#endif
