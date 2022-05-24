// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef SBKNUMPYCHECK_H
#define SBKNUMPYCHECK_H

#include <sbkpython.h>
#include <shibokenmacros.h>


// This header provides a PyArray_Check() definition that can be used to avoid
// having to include the numpy headers. When using numpy headers, make sure
// to include this header after them to skip the definition. Also remember
// that import_array() must then be called to initialize numpy.

namespace Shiboken::Numpy
{

/// Check whether the object is a PyArrayObject
/// \param pyIn object
/// \return Whether it is a PyArrayObject
LIBSHIBOKEN_API bool check(PyObject *pyIn);

} //namespace Shiboken::Numpy

#ifndef PyArray_Check
#  define PyArray_Check(op) Shiboken::Numpy::check(op)
#endif

#endif // SBKNUMPYCHECK_H
