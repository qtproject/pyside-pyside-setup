// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef PYSIDE_WATCH_P_H
#define PYSIDE_WATCH_P_H

#include <pysideqmlmacros.h>

#include <sbkpython.h>

namespace PySide::Watch {

// acts as a sentinel to identify decorated functions and to store the property name being watched.
PYSIDEQML_API PyObject *watchAttrName();

PYSIDEQML_API void init(PyObject *module);

} // namespace PySide::Watch

#endif // PYSIDE_WATCH_P_H
