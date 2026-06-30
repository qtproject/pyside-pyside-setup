// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef PEP384IMPL_P_H
#define PEP384IMPL_P_H

#include "sbkpython.h"
#include "shibokenmacros.h"

extern "C"
{

LIBSHIBOKEN_API bool _Pep_IsPrivateName(PyObject *name);
LIBSHIBOKEN_API PyObject *_Pep_TypePrivateMangle(PyTypeObject *obType, PyObject *name);

// Module Initialization
LIBSHIBOKEN_API void Pep384_Init(void);

} // extern "C"

#endif // PEP384IMPL_P_H
