// Copyright (C) 2019 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDESTRINGS_H
#define PYSIDESTRINGS_H

#include <sbkpython.h>

namespace PySide
{
namespace PyName
{
PyObject *qtStaticMetaObject();
PyObject *qtConnect();
PyObject *qtDisconnect();
PyObject *qtEmit();
PyObject *dict_ring();
PyObject *fset();
PyObject *im_func();
PyObject *im_self();
PyObject *name();
PyObject *parameters();
PyObject *property();
PyObject *select_id();
} // namespace PyName
namespace PyMagicName
{
PyObject *code();
PyObject *doc();
PyObject *func();
PyObject *get();
PyObject *name();
PyObject *property_methods();
} // namespace PyMagicName
} // namespace PySide

#endif // PYSIDESTRINGS_H
