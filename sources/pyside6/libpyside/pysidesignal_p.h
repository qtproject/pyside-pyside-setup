// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef PYSIDE_QSIGNAL_P_H
#define PYSIDE_QSIGNAL_P_H

#include <sbkpython.h>

#include <QtCore/qbytearray.h>
#include <QtCore/qlist.h>
#include <QtCore/qobject.h>
#include <QtCore/qpointer.h>

#ifdef Py_GIL_DISABLED
#  include <atomic>
#endif
#include <memory>

struct PySideSignalData
{
    struct Signature
    {
        QByteArray signature; // ','-separated list of parameter types
        unsigned short attributes{0};
        short argCount{0};
    };

    QByteArray signalName;
    QList<Signature> signatures;
    QByteArrayList signalArguments;
};

extern "C"
{
    extern PyTypeObject *PySideSignal_TypeF(void);

    struct PySideSignal {
        PyObject_HEAD
        PySideSignalData *data;
        PyObject *homonymousMethod;
    };

    struct PySideSignalInstance;
}; //extern "C"

struct PySideSignalInstanceShared
{
    QPointer<QObject> source;
    PyTypeObject *sourceType = nullptr;
};

using PySideSignalInstanceSharedPtr = std::shared_ptr<PySideSignalInstanceShared>;

struct PySideSignalInstancePrivate
{
    QByteArray signalName;
    QByteArray signature;
    PySideSignalInstanceSharedPtr shared;
    PyObject *homonymousMethodPvt = nullptr;
    PySideSignalInstance *next = nullptr;
    unsigned short attributes = 0;
    short argCount = 0;
#ifdef Py_GIL_DISABLED
    /// Lazily filled in by initPySideSignalInstancePrivate(), from whichever
    /// thread emits first. Two threads racing it compute the same index from
    /// the same meta object, so the write needs no ordering - it needs a
    /// memory location of its own, so that a concurrent reader sees either -1
    /// or the finished value and never a torn one.
    std::atomic<short> signalIndex{-1};
#else
    short signalIndex = -1; // lazily initialized by initPySideSignalInstancePrivate()
#endif
};

namespace PySide::Signal {

    void            init(PyObject *module);
    bool            connect(PyObject *source, const char *signal, PyObject *callback);
    QByteArray      getTypeName(PyObject *);
    QByteArray      codeCallbackName(PyObject *callback, const QByteArray &funcName);
    QByteArray      voidType();

} // namespace PySide::Signal

#endif
