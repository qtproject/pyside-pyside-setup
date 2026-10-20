// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef PYSIDEQMLREGISTERTYPE_H
#define PYSIDEQMLREGISTERTYPE_H

#include "pysideqmlmacros.h"

#include <sbkpython.h>
#include <QtCore/qtconfigmacros.h>

QT_BEGIN_NAMESPACE
namespace QQmlPrivate
{
struct RegisterTypeAndRevisions;
}
QT_END_NAMESPACE

namespace PySide::Qml
{

PYSIDEQML_API int qmlRegisterType(PyObject *pyObj, const char *uri,
                                  int versionMajor, int versionMinor,
                                  const char *qmlName, const char *noCreationReason = nullptr,
                                  bool creatable = true);

PYSIDEQML_API int qmlRegisterSingletonType(PyObject *pyObj,const char *uri,
                                           int versionMajor, int versionMinor, const char *qmlName,
                                           PyObject *callback, bool isQObject, bool hasCallback);

PYSIDEQML_API int qmlRegisterSingletonInstance(PyObject *pyObj, const char *uri,
                                               int versionMajor, int versionMinor,
                                               const char *qmlName, PyObject *instanceObject);

PYSIDEQML_API PyObject *qmlElementMacro(PyObject *pyObj);

PYSIDEQML_API PyObject *qmlAnonymousMacro(PyObject *pyObj);

PYSIDEQML_API PyObject *qmlSingletonMacro(PyObject *pyObj);

using QuickRegisterItemFunction =
    bool (*)(PyObject *pyObj, QT_PREPEND_NAMESPACE(QQmlPrivate::RegisterTypeAndRevisions) *);

PYSIDEQML_API QuickRegisterItemFunction getQuickRegisterItemFunction();
PYSIDEQML_API void setQuickRegisterItemFunction(QuickRegisterItemFunction function);

} // namespace PySide::Qml

#endif // PYSIDEQMLREGISTERTYPE_H
