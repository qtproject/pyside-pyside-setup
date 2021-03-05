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

#ifndef SHIBOKEN_BUFFER_H
#define SHIBOKEN_BUFFER_H

#include "sbkpython.h"
#include "shibokenmacros.h"

namespace Shiboken
{

namespace Buffer
{
    enum Type {
        ReadOnly,
        WriteOnly,
        ReadWrite
    };

    /**
     * Creates a new Python buffer pointing to a contiguous memory block at
     * \p memory of size \p size.
     */
    LIBSHIBOKEN_API PyObject *newObject(void *memory, Py_ssize_t size, Type type);

    /**
     * Creates a new <b>read only</b> Python buffer pointing to a contiguous memory block at
     * \p memory of size \p size.
     */
    LIBSHIBOKEN_API PyObject *newObject(const void *memory, Py_ssize_t size);

    /**
     * Check if is ok to use \p pyObj as argument in all function under Shiboken::Buffer namespace.
     */
    LIBSHIBOKEN_API bool checkType(PyObject *pyObj);

    /**
     * Returns a pointer to the memory pointed by the buffer \p pyObj, \p size is filled with the buffer
     * size if not null.
     *
     * If the \p pyObj is a non-contiguous buffer a Python error is set.
     */
    LIBSHIBOKEN_API void *getPointer(PyObject *pyObj, Py_ssize_t *size = nullptr);

} // namespace Buffer
} // namespace Shiboken

#endif
