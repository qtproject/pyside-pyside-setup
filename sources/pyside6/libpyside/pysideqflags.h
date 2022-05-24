// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDE_QFLAGS_H
#define PYSIDE_QFLAGS_H

#include <sbkpython.h>
#include "pysidemacros.h"


extern "C"
{
    struct PYSIDE_API PySideQFlagsObject {
        PyObject_HEAD
        long ob_value;
    };

    PYSIDE_API PyObject* PySideQFlags_tp_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
    PYSIDE_API PyObject* PySideQFlags_tp_richcompare(PyObject *self, PyObject *other, int op);
}


namespace PySide
{
namespace QFlags
{
    /**
     * Creates a new QFlags type.
     */
    PYSIDE_API PyTypeObject *create(const char* name, PyType_Slot *numberMethods);
    /**
     * Creates a new QFlags instance of type \p type and value \p value.
     */
    PYSIDE_API PySideQFlagsObject* newObject(long value, PyTypeObject* type);
    /**
     * Returns the value held by a QFlag.
     */
    PYSIDE_API long getValue(PySideQFlagsObject* self);
}
}

#endif

