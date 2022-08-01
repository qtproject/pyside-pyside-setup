// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include "pysideqmlmetacallerror_p.h"

#include <sbkpython.h>
#include <sbkstring.h>
#include <autodecref.h>

// Remove deprecated MACRO of copysign for MSVC #86286
// https://github.com/python/cpython/issues/86286
#ifdef copysign
#  undef copysign
#endif

#include <QtCore/QObject>
#include <QtCore/QString>

#include <QtQml/QQmlEngine>
#include <QtQml/QQmlListProperty>

#if __has_include (<private/qv4engine_p.h>)
#  define QML_PRIVATE_API_SUPPORT
#  include <private/qv4engine_p.h>
#  include <private/qv4context_p.h>
#  include <private/qqmldata_p.h>
#endif

namespace PySide::Qml {

std::optional<int> qmlMetaCallErrorHandler(QObject *object)
{
#ifdef QML_PRIVATE_API_SUPPORT
    // This JS engine grabber based off of Qt 5.5's `qjsEngine` function
    QQmlData *data = QQmlData::get(object, false);
    if (!data || data->jsWrapper.isNullOrUndefined())
        return {};

    QV4::ExecutionEngine *engine = data->jsWrapper.engine();
    if (engine->currentStackFrame == nullptr)
        return {};

    PyObject *errType, *errValue, *errTraceback;
    PyErr_Fetch(&errType, &errValue, &errTraceback);
    // PYSIDE-464: The error is only valid before PyErr_Restore,
    // PYSIDE-464: therefore we take local copies.
    Shiboken::AutoDecRef objStr(PyObject_Str(errValue));
    const QString errString = QLatin1String(Shiboken::String::toCString(objStr));
    const bool isSyntaxError = errType == PyExc_SyntaxError;
    const bool isTypeError = errType == PyExc_TypeError;
    PyErr_Restore(errType, errValue, errTraceback);

    PyErr_Print();    // Note: PyErr_Print clears the error.

    if (isSyntaxError)
        return engine->throwSyntaxError(errString);
    if (isTypeError)
        return engine->throwTypeError(errString);
    return engine->throwError(errString);
#else
    Q_UNUSED(object);
    qWarning("libpyside6qml was built without QML private API support, error handling will not work.");
    return {};
#endif //  QML_PRIVATE_API_SUPPORT
}

} // namespace PySide::Qml
