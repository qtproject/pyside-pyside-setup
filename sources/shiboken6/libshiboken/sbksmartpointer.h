// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef SBK_SBKSMARTPOINTER_H
#define SBK_SBKSMARTPOINTER_H

#include "sbkpython.h"
#include "shibokenmacros.h"

namespace Shiboken::SmartPointer
{

LIBSHIBOKEN_API PyObject *repr(PyObject *pointer, PyObject *pointee);
LIBSHIBOKEN_API PyObject *dir(PyObject *pointer, PyObject *pointee);

} // namespace Shiboken::SmartPointer

#endif // SBK_SBKSMARTPOINTER_H
