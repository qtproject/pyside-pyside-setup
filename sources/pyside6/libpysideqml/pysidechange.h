// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef PYSIDEQML_CHANGE_H
#define PYSIDEQML_CHANGE_H

#include <pysideqmlmacros.h>

#include <sbkpython.h>

extern "C"
{
PYSIDEQML_API PyTypeObject *PySideChange_TypeF(void);
} // extern "C"

namespace PySide::Change {

PYSIDEQML_API void init(PyObject *module);

} // namespace PySide::Change

#endif // PYSIDEQML_CHANGE_H
