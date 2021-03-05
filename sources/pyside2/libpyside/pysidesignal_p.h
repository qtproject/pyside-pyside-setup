/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:COMM$
**
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** $QT_END_LICENSE$
**
****************************************************************************/

#ifndef PYSIDE_QSIGNAL_P_H
#define PYSIDE_QSIGNAL_P_H

#include <sbkpython.h>

#include <QtCore/QByteArray>
#include <QtCore/QVector>

struct PySideSignalData
{
    struct Signature
    {
        QByteArray signature;
        int attributes;
    };

    QByteArray signalName;
    QVector<Signature> signatures;
    QByteArrayList *signalArguments;
};

extern "C"
{
    extern PyTypeObject *PySideSignalTypeF(void);

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

namespace PySide { namespace Signal {

    void            init(PyObject *module);
    bool            connect(PyObject *source, const char *signal, PyObject *callback);
    QByteArray      getTypeName(PyObject *);
    QString         codeCallbackName(PyObject *callback, const QString &funcName);
    QByteArray      voidType();

}} //namespace PySide

#endif
