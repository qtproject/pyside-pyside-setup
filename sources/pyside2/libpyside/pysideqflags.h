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

    PYSIDE_API PyObject* PySideQFlagsNew(PyTypeObject *type, PyObject *args, PyObject *kwds);
    PYSIDE_API PyObject* PySideQFlagsRichCompare(PyObject *self, PyObject *other, int op);
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

