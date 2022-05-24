// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include "shibokenbuffer.h"
#include <cstdlib>
#include <cstring>

bool Shiboken::Buffer::checkType(PyObject *pyObj)
{
    return PyObject_CheckBuffer(pyObj) != 0;
}

void *Shiboken::Buffer::getPointer(PyObject *pyObj, Py_ssize_t *size)
{
    Py_buffer view;
    if (PyObject_GetBuffer(pyObj, &view, PyBUF_ND) == 0) {
        if (size)
            *size = view.len;
        PyBuffer_Release(&view);
        return view.buf;
    }
    return nullptr;
}

void *Shiboken::Buffer::copyData(PyObject *pyObj, Py_ssize_t *sizeIn)
{
    void *result = nullptr;
    Py_ssize_t size = 0;

    Py_buffer view;
    if (PyObject_GetBuffer(pyObj, &view, PyBUF_ND) == 0) {
        size = view.len;
        if (size) {
            result = std::malloc(size);
            if (result != nullptr)
                std::memcpy(result, view.buf, size);
            else
                size = 0;
        }
        PyBuffer_Release(&view);
    }

    if (sizeIn != nullptr)
        *sizeIn = size;
    return result;
}

PyObject *Shiboken::Buffer::newObject(void *memory, Py_ssize_t size, Type type)
{
    if (size == 0)
        Py_RETURN_NONE;
    Py_buffer view;
    memset(&view, 0, sizeof(Py_buffer));
    view.buf = memory;
    view.len = size;
    view.readonly = type == Shiboken::Buffer::ReadOnly;
    view.ndim = 1;
    view.itemsize = sizeof(char);
    Py_ssize_t shape[] = { size };
    view.shape = shape;
    // Pep384: This is way too complicated and impossible with the limited api:
    //return PyMemoryView_FromBuffer(&view);
    return PyMemoryView_FromMemory(reinterpret_cast<char *>(view.buf),
                                   size, type == ReadOnly ? PyBUF_READ : PyBUF_WRITE);
}

PyObject *Shiboken::Buffer::newObject(const void *memory, Py_ssize_t size)
{
    return newObject(const_cast<void *>(memory), size, ReadOnly);
}
