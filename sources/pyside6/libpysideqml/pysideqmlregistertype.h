// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDEQMLREGISTERTYPE_H
#define PYSIDEQMLREGISTERTYPE_H

#include "pysideqmlmacros.h"

#include <sbkpython.h>

namespace QQmlPrivate
{
struct RegisterType;
}

namespace PySide::Qml
{

/**
 * PySide implementation of qmlRegisterType<T> function.
 *
 * \param pyObj Python type to be registered.
 * \param uri QML element uri.
 * \param versionMajor QML component major version.
 * \param versionMinor QML component minor version.
 * \param qmlName QML element name
 * \return the metatype id of the registered type.
 */
PYSIDEQML_API int qmlRegisterType(PyObject *pyObj, const char *uri,
                                  int versionMajor, int versionMinor,
                                  const char *qmlName, const char *noCreationReason = nullptr,
                                  bool creatable = true);

/**
 * PySide implementation of qmlRegisterSingletonType<T> function.
 *
 * \param pyObj Python type to be registered.
 * \param uri QML element uri.
 * \param versionMajor QML component major version.
 * \param versionMinor QML component minor version.
 * \param qmlName QML element name
 * \param callback Registration callback
 * \return the metatype id of the registered type.
 */
PYSIDEQML_API int qmlRegisterSingletonType(PyObject *pyObj,const char *uri,
                                           int versionMajor, int versionMinor, const char *qmlName,
                                           PyObject *callback, bool isQObject, bool hasCallback);

/**
 * PySide implementation of qmlRegisterSingletonInstance<T> function.
 *
 * \param pyObj Python type to be registered.
 * \param uri QML element uri.
 * \param versionMajor QML component major version.
 * \param versionMinor QML component minor version.
 * \param qmlName QML element name
 * \param instanceObject singleton object to be registered.
 * \return the metatype id of the registered type.
 */
PYSIDEQML_API int qmlRegisterSingletonInstance(PyObject *pyObj, const char *uri,
                                               int versionMajor, int versionMinor,
                                               const char *qmlName, PyObject *instanceObject);

/**
 * PySide implementation of the QML_ELEMENT macro
 *
 * \param pyObj Python type to be registered
 */
PYSIDEQML_API PyObject *qmlElementMacro(PyObject *pyObj);

/// PySide implementation of the QML_ANONYMOUS macro
/// \param pyObj Python type to be registered
PYSIDEQML_API PyObject *qmlAnonymousMacro(PyObject *pyObj);

/// PySide implementation of the QML_SINGLETON macro
/// \param pyObj Python type to be registered
PYSIDEQML_API PyObject *qmlSingletonMacro(PyObject *pyObj);


// Used by QtQuick module to fill the QQmlPrivate::RegisterType::parserStatusCast,
// valueSourceCast and valueInterceptorCast fields with the correct values.
using QuickRegisterItemFunction =
    bool (*)(PyObject *pyObj, QQmlPrivate::RegisterType *);

PYSIDEQML_API QuickRegisterItemFunction getQuickRegisterItemFunction();
PYSIDEQML_API void setQuickRegisterItemFunction(QuickRegisterItemFunction function);

} // namespace PySide::Qml

#endif // PYSIDEQMLREGISTERTYPE_H
