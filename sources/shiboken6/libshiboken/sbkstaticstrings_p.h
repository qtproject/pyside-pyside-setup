// Copyright (C) 2019 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include "sbkpython.h"
#include "shibokenmacros.h"

namespace Shiboken
{
namespace PyName
{
PyObject *classmethod();
PyObject *compile();
PyObject *function();
PyObject *marshal();
PyObject *method();
PyObject *mro();
PyObject *overload();
PyObject *qApp();
PyObject *staticmethod();
} // namespace PyName
namespace PyMagicName
{
PyObject *base();
PyObject *bases();
PyObject *builtins();
PyObject *code();
PyObject *dictoffset();
PyObject *func_kind();
PyObject *iter();
PyObject *module();
PyObject *mro();
PyObject *new_();
PyObject *objclass();
PyObject *signature();
PyObject *weakrefoffset();
} // namespace PyMagicName
} // namespace Shiboken
