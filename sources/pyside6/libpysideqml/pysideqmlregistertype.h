/****************************************************************************
**
** Copyright (C) 2016 The Qt Company Ltd.
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
