// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef PYSIDE_COMPUTED_P_H
#define PYSIDE_COMPUTED_P_H

#include <pysideqmlmacros.h>

#include <sbkpython.h>

namespace PySide::Computed {

// Attribute name set on decorated functions to store computed metadata
PYSIDEQML_API PyObject *computedAttrName();

PYSIDEQML_API void init(PyObject *module);

} // namespace PySide::Computed

#endif // PYSIDE_COMPUTED_P_H
