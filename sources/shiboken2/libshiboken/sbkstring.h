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

#ifndef SBKSTRING_H
#define SBKSTRING_H

#include "sbkpython.h"
#include "shibokenmacros.h"

namespace Shiboken
{
namespace String
{
    LIBSHIBOKEN_API bool check(PyObject *obj);
    LIBSHIBOKEN_API bool checkIterable(PyObject *obj);
    LIBSHIBOKEN_API bool checkType(PyTypeObject *obj);
    LIBSHIBOKEN_API bool checkChar(PyObject *obj);
    LIBSHIBOKEN_API bool isConvertible(PyObject *obj);
    LIBSHIBOKEN_API PyObject *fromCString(const char *value);
    LIBSHIBOKEN_API PyObject *fromCString(const char *value, int len);
    LIBSHIBOKEN_API const char *toCString(PyObject *str, Py_ssize_t *len = nullptr);
    LIBSHIBOKEN_API bool concat(PyObject **val1, PyObject *val2);
    LIBSHIBOKEN_API PyObject *fromFormat(const char *format, ...);
    LIBSHIBOKEN_API PyObject *fromStringAndSize(const char *str, Py_ssize_t size);
    LIBSHIBOKEN_API int compare(PyObject *val1, const char *val2);
    LIBSHIBOKEN_API Py_ssize_t len(PyObject *str);
    LIBSHIBOKEN_API PyObject *createStaticString(const char *str);
    LIBSHIBOKEN_API PyObject *getSnakeCaseName(const char *name, bool lower);
    LIBSHIBOKEN_API PyObject *getSnakeCaseName(PyObject *name, bool lower);

} // namespace String
} // namespace Shiboken


#endif


