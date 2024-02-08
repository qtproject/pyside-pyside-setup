// Copyright (C) 2024 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDEQSLOTOBJECT_P_H
#define PYSIDEQSLOTOBJECT_P_H

#include "pysidemacros.h"
#include <sbkpython.h>

#include <QtCore/QObject>
#include <QtCore/qobjectdefs.h>

namespace PySide
{

class PySideQSlotObject : public QtPrivate::QSlotObjectBase
{
    PyObject *callable;

    static void impl(int which, QSlotObjectBase *this_, QObject *receiver, void **args, bool *ret);

public:
    PySideQSlotObject(PyObject *callable) : QtPrivate::QSlotObjectBase(&impl), callable(callable)
    {
        Py_INCREF(callable);
    }

    ~PySideQSlotObject()
    {
        auto gstate = PyGILState_Ensure();
        Py_DECREF(callable);
        PyGILState_Release(gstate);
    }
};


} // namespace PySide

#endif // PYSIDEQSLOTOBJECT_P_H
