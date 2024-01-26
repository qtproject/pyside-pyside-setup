// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef CORE_SNIPPETS_P_H
#define CORE_SNIPPETS_P_H

#include "pysidemacros.h"

#include <sbkpython.h>

#include <QtCore/qnamespace.h>

#include <functional>

QT_FORWARD_DECLARE_CLASS(QGenericArgument)
QT_FORWARD_DECLARE_CLASS(QGenericReturnArgument)
QT_FORWARD_DECLARE_CLASS(QMetaType)
QT_FORWARD_DECLARE_CLASS(QObject)
QT_FORWARD_DECLARE_CLASS(QRegularExpression)
QT_FORWARD_DECLARE_CLASS(QVariant);

QT_BEGIN_NAMESPACE
namespace QtCoreHelper {
class QGenericArgumentHolder;
class QGenericReturnArgumentHolder;
}
QT_END_NAMESPACE

// Helpers for QVariant conversion

QMetaType QVariant_resolveMetaType(PyTypeObject *type);

QVariant QVariant_convertToValueList(PyObject *list);

bool QVariant_isStringList(PyObject *list);

// Helpers for qAddPostRoutine
namespace PySide {
void globalPostRoutineCallback();
void addPostRoutine(PyObject *callback);
}

// Helpers for QObject::findChild(ren)()
QObject *qObjectFindChild(const QObject *parent, const QString &name,
                          PyTypeObject *desiredType, Qt::FindChildOptions options);

using FindChildHandler = std::function<void(QObject *)>;

void qObjectFindChildren(const QObject *parent, const QString &name,
                         PyTypeObject *desiredType, Qt::FindChildOptions options,
                         FindChildHandler handler);

void qObjectFindChildren(const QObject *parent, const QRegularExpression &pattern,
                         PyTypeObject *desiredType, Qt::FindChildOptions options,
                         FindChildHandler handler);

// Helpers for translation
QString qObjectTr(PyTypeObject *type, const char *sourceText, const char *disambiguation, int n);

bool PyDate_ImportAndCheck(PyObject *pyIn);
bool PyDateTime_ImportAndCheck(PyObject *pyIn);
bool PyTime_ImportAndCheck(PyObject *pyIn);

// Helpers for QMetaObject::invokeMethod(), QMetaMethod::invoke(). The std::function
// serves to abstract from QMetaObject/QMetaMethod invocation parameters.
using InvokeMetaMethodFunc =
    std::function<bool(QGenericArgument,QGenericArgument,QGenericArgument,QGenericArgument,
                       QGenericArgument,QGenericArgument,QGenericArgument,QGenericArgument,
                       QGenericArgument,QGenericArgument)>;

using InvokeMetaMethodFuncWithReturn =
    std::function<bool(QGenericReturnArgument,
                       QGenericArgument,QGenericArgument,QGenericArgument,QGenericArgument,
                       QGenericArgument,QGenericArgument,QGenericArgument,QGenericArgument,
                       QGenericArgument,QGenericArgument)>;

// Call a void meta method from Python passing the argument holder helpers.
PyObject *invokeMetaMethod(const InvokeMetaMethodFunc &f,
                           const QtCoreHelper::QGenericArgumentHolder &,
                           const QtCoreHelper::QGenericArgumentHolder &,
                           const QtCoreHelper::QGenericArgumentHolder &,
                           const QtCoreHelper::QGenericArgumentHolder &,
                           const QtCoreHelper::QGenericArgumentHolder &,
                           const QtCoreHelper::QGenericArgumentHolder &,
                           const QtCoreHelper::QGenericArgumentHolder &,
                           const QtCoreHelper::QGenericArgumentHolder &,
                           const QtCoreHelper::QGenericArgumentHolder &,
                           const QtCoreHelper::QGenericArgumentHolder &);

// Call a meta method with a return value from Python passing the argument holder
// helpers.
PyObject *invokeMetaMethodWithReturn(const InvokeMetaMethodFuncWithReturn &f,
                                     const QtCoreHelper::QGenericReturnArgumentHolder &,
                                     const QtCoreHelper::QGenericArgumentHolder &,
                                     const QtCoreHelper::QGenericArgumentHolder &,
                                     const QtCoreHelper::QGenericArgumentHolder &,
                                     const QtCoreHelper::QGenericArgumentHolder &,
                                     const QtCoreHelper::QGenericArgumentHolder &,
                                     const QtCoreHelper::QGenericArgumentHolder &,
                                     const QtCoreHelper::QGenericArgumentHolder &,
                                     const QtCoreHelper::QGenericArgumentHolder &,
                                     const QtCoreHelper::QGenericArgumentHolder &,
                                     const QtCoreHelper::QGenericArgumentHolder &);

#endif // CORE_SNIPPETS_P_H
