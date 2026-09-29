// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef SBKCPPTONUMPY_H
#define SBKCPPTONUMPY_H

#include <sbkpython.h>
#include <shibokenmacros.h>

#include <cstdint>

namespace Shiboken::Numpy
{

/*!
    Creates a one-dimensional numpy array (PyArrayObject) of type uint8/NPY_BYTE
    of \a size from \a data.
*/
LIBSHIBOKEN_API PyObject *createByteArray1(Py_ssize_t size, const uint8_t *data);

/*!
    Creates a one-dimensional numpy array (PyArrayObject) of type double/NPY_DOUBLE
    of \a size from \a data.
*/
LIBSHIBOKEN_API PyObject *createDoubleArray1(Py_ssize_t size, const double *data);

/*!
    Creates a one-dimensional numpy array (PyArrayObject) of type float/NPY_FLOAT
    of \a size from \a data.
*/
LIBSHIBOKEN_API PyObject *createFloatArray1(Py_ssize_t size, const float *data);

/*!
    Creates a one-dimensional numpy array (PyArrayObject) of type int/NPY_INT
    of \a size from \a data.
*/
LIBSHIBOKEN_API PyObject *createIntArray1(Py_ssize_t size, const int *data);

} //namespace Shiboken::Numpy

#endif // SBKCPPTONUMPY_H
