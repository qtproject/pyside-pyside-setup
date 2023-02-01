/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:COMM$
**
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** $QT_END_LICENSE$
**
****************************************************************************/

#ifndef SBKSTATICSTRINGS_H
#define SBKSTATICSTRINGS_H

#include "sbkpython.h"
#include "shibokenmacros.h"

namespace Shiboken
{
// Some often-used strings
namespace PyName
{
LIBSHIBOKEN_API PyObject *co_name();
LIBSHIBOKEN_API PyObject *dumps();
LIBSHIBOKEN_API PyObject *fget();
LIBSHIBOKEN_API PyObject *fset();
LIBSHIBOKEN_API PyObject *f_code();
LIBSHIBOKEN_API PyObject *f_lineno();
LIBSHIBOKEN_API PyObject *loads();
LIBSHIBOKEN_API PyObject *multi();
LIBSHIBOKEN_API PyObject *name();
LIBSHIBOKEN_API PyObject *result();
LIBSHIBOKEN_API PyObject *select_id();
LIBSHIBOKEN_API PyObject *underscore();
LIBSHIBOKEN_API PyObject *value();
LIBSHIBOKEN_API PyObject *values();
} // namespace PyName

namespace PyMagicName
{
LIBSHIBOKEN_API PyObject *class_();
LIBSHIBOKEN_API PyObject *dict();
LIBSHIBOKEN_API PyObject *doc();
LIBSHIBOKEN_API PyObject *ecf();
LIBSHIBOKEN_API PyObject *file();
LIBSHIBOKEN_API PyObject *func();
LIBSHIBOKEN_API PyObject *get();
LIBSHIBOKEN_API PyObject *members();
LIBSHIBOKEN_API PyObject *module();
LIBSHIBOKEN_API PyObject *name();
LIBSHIBOKEN_API PyObject *property_methods();
LIBSHIBOKEN_API PyObject *qualname();
LIBSHIBOKEN_API PyObject *self();
} // namespace PyMagicName
} // namespace Shiboken

#endif // SBKSTATICSTRINGS_H
