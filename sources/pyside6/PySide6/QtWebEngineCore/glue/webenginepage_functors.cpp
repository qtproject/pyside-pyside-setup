// Copyright (C) 2024 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include "webenginepage_functors.h"

#include "autodecref.h"
#include "gilstate.h"

#include "pysideutils.h"

#include <QtCore/qvariant.h>

QT_BEGIN_NAMESPACE

void RunJavascriptFunctor::operator()(const QVariant &result)
{
    Shiboken::GilState state;
    Shiboken::AutoDecRef arglist(PyTuple_New(1));
    switch (result.typeId()) {
    case QMetaType::Bool: {
        PyObject *pyValue = result.toBool() ? Py_True : Py_False;
        Py_INCREF(pyValue);
        PyTuple_SET_ITEM(arglist, 0, pyValue);
    }
    break;
    case QMetaType::Int:
    case QMetaType::UInt:
    case QMetaType::LongLong:
    case QMetaType::ULongLong:
    case QMetaType::Double:
        PyTuple_SET_ITEM(arglist, 0, PyFloat_FromDouble(result.toDouble()));
    break;
    default: {
        const QString value = result.toString();
        PyTuple_SET_ITEM(arglist, 0, PySide::qStringToPyUnicode(value));
    }
    break;
    }
    Shiboken::AutoDecRef ret(PyObject_CallObject(object(), arglist));
    release(); // single shot
}

QT_END_NAMESPACE
