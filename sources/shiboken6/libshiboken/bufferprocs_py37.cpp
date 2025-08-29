// Copyright (C) 2018 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

/*****************************************************************************
 *
 * Copied from abstract.c
 *
 * Py_buffer has been replaced by Pep_buffer
 *
 */

#ifdef Py_LIMITED_API

#include "sbkpython.h"
// Buffer C-API for Python 3.0 (copy of cpython/Objects/abstract.c:426)

int
PyObject_GetBuffer(PyObject *obj, Pep_buffer *view, int flags)
{
    PyBufferProcs *pb = PepType_AS_BUFFER(Py_TYPE(obj));

    if (pb == NULL || pb->bf_getbuffer == NULL) {
        PyErr_Format(PyExc_TypeError,
                     "a bytes-like object is required, not '%.100s'",
                     Py_TYPE(obj)->tp_name);
        return -1;
    }
    return (*pb->bf_getbuffer)(obj, view, flags);
}

// Omitted functions: _IsFortranContiguous(), _IsCContiguous(), PyBuffer_IsContiguous(),
// PyBuffer_GetPointer(),// _Py_add_one_to_index_F(), _Py_add_one_to_index_C(),
// PyBuffer_FromContiguous(), PyObject_CopyData(), PyBuffer_FillContiguousStrides(),
// PyBuffer_FillInfo()

void
PyBuffer_Release(Pep_buffer *view)
{
    PyObject *obj = view->obj;
    PyBufferProcs *pb;
    if (obj == NULL)
        return;
    pb = PepType_AS_BUFFER(Py_TYPE(obj));
    if (pb && pb->bf_releasebuffer)
        pb->bf_releasebuffer(obj, view);
    view->obj = NULL;
    Py_DECREF(obj);
}

#endif // Py_LIMITED_API
