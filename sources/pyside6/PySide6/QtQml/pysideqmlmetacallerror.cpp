/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
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

#include "pysideqmlmetacallerror_p.h"

#include <sbkpython.h>
#include <sbkstring.h>
#include <autodecref.h>

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

namespace PySide {

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
    return {};
#endif //  QML_PRIVATE_API_SUPPORT
}

} // namespace PySide
