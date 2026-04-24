// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef SBKFEATURE_BASE_H
#define SBKFEATURE_BASE_H

#include "sbkpython.h"
#include "shibokenmacros.h"

extern "C"
{

LIBSHIBOKEN_API int currentSelectId(PyTypeObject *type);
LIBSHIBOKEN_API PyObject *mangled_type_getattro(PyTypeObject *type, PyObject *name);
LIBSHIBOKEN_API PyObject *Sbk_TypeGet___dict__(PyTypeObject *type, void *context);
LIBSHIBOKEN_API PyObject *SbkObject_GenericGetAttr(PyObject *obj, PyObject *name);
LIBSHIBOKEN_API int SbkObject_GenericSetAttr(PyObject *obj, PyObject *name, PyObject *value);

} // extern "C"

#endif // SBKFEATURE_BASE_H
