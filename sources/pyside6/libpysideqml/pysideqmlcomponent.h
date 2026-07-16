// Copyright (C) 2026 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef PYSIDEQMLCOMPONENT_H
#define PYSIDEQMLCOMPONENT_H

#include <pysideqmlmacros.h>
#include <sbkpython.h>

namespace PySide::QmlComponent {

PYSIDEQML_API void init(PyObject *module);

} // namespace PySide::QmlComponent

#endif // PYSIDEQMLCOMPONENT_H
