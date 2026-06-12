// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef PYSIDE_AUTOPROPERTIES_H
#define PYSIDE_AUTOPROPERTIES_H

#include <pysideqmlmacros.h>
#include <sbkpython.h>

namespace PySide::AutoProperties {

PYSIDEQML_API void init(PyObject *module);

} // namespace PySide::AutoProperties

#endif // PYSIDE_AUTOPROPERTIES_H
