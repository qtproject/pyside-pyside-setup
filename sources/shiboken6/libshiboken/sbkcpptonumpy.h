// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef SBKCPPTONUMPY_H
#define SBKCPPTONUMPY_H

#include <sbkpython.h>
#include <shibokenmacros.h>

#include <cstdint>

namespace Shiboken::Numpy
{

/// Create a one-dimensional numpy array of type uint8/NPY_BYTE
/// \param size Size
/// \param data Data
/// \return PyArrayObject
LIBSHIBOKEN_API PyObject *createByteArray1(Py_ssize_t size, const uint8_t *data);

/// Create a one-dimensional numpy array of type double/NPY_DOUBLE
/// \param size Size
/// \param data Data
/// \return PyArrayObject
LIBSHIBOKEN_API PyObject *createDoubleArray1(Py_ssize_t size, const double *data);

/// Create a one-dimensional numpy array of type float/NPY_FLOAT
/// \param size Size
/// \param data Data
/// \return PyArrayObject
LIBSHIBOKEN_API PyObject *createFloatArray1(Py_ssize_t size, const float *data);

/// Create a one-dimensional numpy array of type int/NPY_INT
/// \param size Size
/// \param data Data
/// \return PyArrayObject
LIBSHIBOKEN_API PyObject *createIntArray1(Py_ssize_t size, const int *data);

} //namespace Shiboken::Numpy

#endif // SBKCPPTONUMPY_H
