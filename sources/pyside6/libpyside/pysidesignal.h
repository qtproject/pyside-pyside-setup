// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef PYSIDE_SIGNAL_H
#define PYSIDE_SIGNAL_H

#include <pysidemacros.h>

#include <sbkpython.h>

#include <QtCore/qlist.h>

QT_BEGIN_NAMESPACE
class QMetaMethod;
class QObject;
QT_END_NAMESPACE

extern "C"
{
    extern PYSIDE_API PyTypeObject *PySideSignal_TypeF(void);
    extern PYSIDE_API PyTypeObject *PySideSignalInstance_TypeF(void);

    // Internal object
    struct PYSIDE_API PySideSignal;

    struct PySideSignalInstancePrivate;
    struct PYSIDE_API PySideSignalInstance
    {
        PyObject_HEAD
        PySideSignalInstancePrivate *d;
    };
}; // extern "C"

namespace PySide::Signal {

/*!
    Returns whether \a pyObj is a PySideSignal.
*/
PYSIDE_API bool checkType(PyObject *pyObj);

/*!
    Returns whether \a pyObj is a PySideSignalInstance.
*/
PYSIDE_API bool checkInstanceType(PyObject *pyObj);

/*!
    Registers all C++ signals of the QObject meta object \a metaObject on
    the Python type \a pyObj.
*/
PYSIDE_API void registerSignals(PyTypeObject *pyObj, const QMetaObject *metaObject);

PYSIDE_API PySideSignalInstance *newObjectFromMethod(QObject *sourceQObject, PyObject *source,
                                                     const QList<QMetaMethod> &methods);

PYSIDE_API PySideSignalInstance *initialize(PySideSignal *self, PyObject *name, PyObject *object);

/*!
    Returns the internal reference to the object to which the
    \a signal is attached.
*/
PYSIDE_API PyObject *getObject(PySideSignalInstance *signal);

/*!
    Returns the signature of the \a signal.
*/
PYSIDE_API const char *getSignature(PySideSignalInstance *signal);

struct EmitterData
{
    QObject *emitter = nullptr;
    int methodIndex = -1;
};

/*!
    A convenience to retrieve the emitter data from the signal instance
    \a signal.
*/
PYSIDE_API EmitterData getEmitterData(PySideSignalInstance *signal);

/*!
    Updates the signal instances in the instance dictionary of the
    Python object \a source from the signals found in its type's MRO.
*/
PYSIDE_API void updateSourceObject(PyObject *source);

/*!
    Returns whether the \a signature is a Qt signal based on the
    \c SIGNAL flag.
*/
PYSIDE_API bool isQtSignal(const char *signature);

/*!
    Returns whether the \a signature is a Qt signal. This function is
    similar to isQtSignal(), however if it fails, it raises a Python error.
*/
PYSIDE_API bool checkQtSignal(const char *signature);

PYSIDE_API QByteArray getCallbackSignature(QMetaMethod signal, QObject *receiver,
                                           PyObject *callback, bool encodeName);
} // namespace PySide::Signal

#endif
