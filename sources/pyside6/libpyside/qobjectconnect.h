// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef QOBJECTCONNECT_H
#define QOBJECTCONNECT_H

#include "pysidemacros.h"

#include <sbkpython.h>

#include <QtCore/qmetaobject.h>

QT_FORWARD_DECLARE_CLASS(QObject)
QT_FORWARD_DECLARE_CLASS(QMetaMethod)

namespace PySide
{

/*!
    Helper for QObject::connect(): Makes a string-based connection
    of type \a type from the \a signal of \a source to the \a slot
    of \a receiver.
*/
PYSIDE_API QMetaObject::Connection
    qobjectConnect(QObject *source, const char *signal,
               QObject *receiver, const char *slot,
               Qt::ConnectionType type);

/*!
    \overload
    Helper for QObject::connect(): Makes a connection based on QMetaMethod
    of type \a type from the \a signal of \a source to the \a slot
    of \a receiver.
*/
PYSIDE_API QMetaObject::Connection
    qobjectConnect(QObject *source, QMetaMethod signal,
                   QObject *receiver, QMetaMethod slot,
                   Qt::ConnectionType type);

/*!
    Helper for QObject::connect(): Makes a connection of type \a type
    from the \a signal of \a source to a Python \a callback.
*/
PYSIDE_API QMetaObject::Connection
    qobjectConnectCallback(QObject *source, const char *signal,
                           PyObject *callback, Qt::ConnectionType type);

/*!
    \overload
    Helper for QObject::connect(): Makes a connection of type \a type
    from the \a signal of \a source to a Python \a callback and a
    \a context object.
*/
PYSIDE_API QMetaObject::Connection
    qobjectConnectCallback(QObject *source, const char *signal, QObject *context,
                           PyObject *callback, Qt::ConnectionType type);

/*!
    Helper for QObject::disconnect(): Disconnects a Python \a callback
    from the \a signal of \a source.
    Returns whether the disconnection succeeded.
*/
PYSIDE_API bool qobjectDisconnectCallback(QObject *source, const char *signal,
                                          PyObject *callback);

/*!
    Helper for functions that forward arguments to QObject::connect(),
    for example, QTimer::singleShot(). Connects the \a signal of
    \a self to \a argument, which can be a signal or a callable.
    Returns whether the connection succeeded.
*/
PYSIDE_API bool callConnect(PyObject *self, const char *signal, PyObject *argument);

} // namespace PySide

#endif // QOBJECTCONNECT_H
