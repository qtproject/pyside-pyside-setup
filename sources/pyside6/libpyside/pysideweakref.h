// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef __PYSIDEWEAKREF__
#define __PYSIDEWEAKREF__

#include <pysidemacros.h>
#include <sbkpython.h>

typedef void (*PySideWeakRefFunction)(void* userData);

namespace PySide { namespace WeakRef {

PYSIDE_API PyObject* create(PyObject* ob, PySideWeakRefFunction func, void* userData);

} //PySide
} //WeakRef


#endif
