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

#ifndef PYTHON25COMPAT_H
#define PYTHON25COMPAT_H
#include "sbkpython.h"
#include <cstring>

/*
 *The #defines below were taken from Cython-generated code to allow shiboken to be used with python2.5.
 * Maybe not all of these defines are useful to us, time will tell which ones are really needed or not.
 */

#if PY_VERSION_HEX < 0x02060000
#define Py_REFCNT(ob) (((PyObject *)(ob))->ob_refcnt)
#define Py_TYPE(ob)   (((PyObject *)(ob))->ob_type)
#define Py_SIZE(ob)   (((PyVarObject *)(ob))->ob_size)
#define PyVarObject_HEAD_INIT(type, size) \
        PyObject_HEAD_INIT(type) size,
#define PyType_Modified(t)

typedef struct {
    void *buf;
    PyObject *obj;
    Py_ssize_t len;
    Py_ssize_t itemsize;
    int readonly;
    int ndim;
    char *format;
    Py_ssize_t *shape;
    Py_ssize_t *strides;
    Py_ssize_t *suboffsets;
    void *internal;
} Py_buffer;

#define PyBUF_SIMPLE 0
#define PyBUF_WRITABLE 0x0001
#define PyBUF_LOCK 0x0002
#define PyBUF_FORMAT 0x0004
#define PyBUF_ND 0x0008
#define PyBUF_STRIDES (0x0010 | PyBUF_ND)
#define PyBUF_C_CONTIGUOUS (0x0020 | PyBUF_STRIDES)
#define PyBUF_F_CONTIGUOUS (0x0040 | PyBUF_STRIDES)
#define PyBUF_ANY_CONTIGUOUS (0x0080 | PyBUF_STRIDES)
#define PyBUF_INDIRECT (0x0100 | PyBUF_STRIDES)

#define PyBytes_Check PyString_Check
#define PyBytes_FromString PyString_FromString
#define PyBytes_FromFormat PyString_FromFormat
#define PyBytes_FromStringAndSize PyString_FromStringAndSize
#define PyBytes_GET_SIZE PyString_GET_SIZE
#define PyBytes_AS_STRING PyString_AS_STRING
#define PyBytes_AsString PyString_AsString
#define PyBytes_Concat PyString_Concat
#define PyBytes_Size PyString_Size

inline PyObject *PyUnicode_FromString(const char *s)
{
    std::size_t len = std::strlen(s);
    return PyUnicode_DecodeUTF8(s, len, 0);
}

#define PyLong_FromSize_t _PyLong_FromSize_t
#define PyLong_AsSsize_t _PyLong_AsSsize_t

#endif

#endif
