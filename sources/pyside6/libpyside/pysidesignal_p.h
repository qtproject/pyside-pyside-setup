// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDE_QSIGNAL_P_H
#define PYSIDE_QSIGNAL_P_H

#include <sbkpython.h>

#include <QtCore/QByteArray>
#include <QtCore/QList>

struct PySideSignalData
{
    struct Signature
    {
        QByteArray signature;
        int attributes;
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

struct PySideSignalInstancePrivate
{
    QByteArray signalName;
    QByteArray signature;
    int attributes = 0;
    PyObject *source = nullptr;
    PyObject *homonymousMethod = nullptr;
    PySideSignalInstance *next = nullptr;
};

namespace PySide::Signal {

    void            init(PyObject *module);
    bool            connect(PyObject *source, const char *signal, PyObject *callback);
    QByteArray      getTypeName(PyObject *);
    QString         codeCallbackName(PyObject *callback, const QString &funcName);
    QByteArray      voidType();

} // namespace PySide::Signal

#endif
