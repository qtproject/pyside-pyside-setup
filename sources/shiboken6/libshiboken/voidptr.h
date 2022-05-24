// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef VOIDPTR_H
#define VOIDPTR_H

#include "sbkpython.h"
#include "shibokenmacros.h"
#include "sbkconverter.h"

extern "C"
{

// Void pointer type declaration.
extern LIBSHIBOKEN_API PyTypeObject *SbkVoidPtr_TypeF(void);

} // extern "C"

namespace VoidPtr
{

void init();
SbkConverter *createConverter();
LIBSHIBOKEN_API void addVoidPtrToModule(PyObject *module);

LIBSHIBOKEN_API void setSize(PyObject *voidPtr, Py_ssize_t size);
LIBSHIBOKEN_API Py_ssize_t getSize(PyObject *voidPtr);
LIBSHIBOKEN_API bool isWritable(PyObject *voidPtr);
LIBSHIBOKEN_API void setWritable(PyObject *voidPtr, bool isWritable);
}


#endif // VOIDPTR_H
