// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDEQMLVOLATILEBOOL_H
#define PYSIDEQMLVOLATILEBOOL_H

#include <sbkpython.h>

PyTypeObject *QtQml_VolatileBool_TypeF(void);

#define VolatileBool_Check(op) (Py_TYPE(op) == QtQml_VolatileBool_TypeF())

void initQtQmlVolatileBool(PyObject *module);

#endif // PYSIDEQMLVOLATILEBOOL_H
