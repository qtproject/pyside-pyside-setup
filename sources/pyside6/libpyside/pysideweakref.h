// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef __PYSIDEWEAKREF__
#define __PYSIDEWEAKREF__

#include <pysidemacros.h>
#include <sbkpython.h>

using PySideWeakRefFunction = void (*)(void *userData);

namespace PySide::WeakRef {

PYSIDE_API PyObject* create(PyObject* ob, PySideWeakRefFunction func, void* userData);

} // namespace PySide::WeakRef

#endif
