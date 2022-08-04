// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

// included by sbknumpy.cpp

namespace Shiboken::Numpy {

#ifdef HAVE_NUMPY

// Helper to create a 1-dimensional numpy array
template <class Type>
static PyObject *_createArray1(Py_ssize_t size, int numpyType, const Type *data)
{
    const npy_intp dims[1] = {size};
    PyObject *result = PyArray_EMPTY(1, dims, numpyType, 0);
    auto *array = reinterpret_cast<PyArrayObject *>(result);
    auto *rawTargetData = PyArray_DATA(array);
    auto *targetData = reinterpret_cast<Type *>(rawTargetData);
    std::copy(data, data + size, targetData);
    return result;
}

PyObject *createByteArray1(Py_ssize_t size, const uint8_t *data)
{
    return _createArray1(size, NPY_BYTE, data);
}

PyObject *createDoubleArray1(Py_ssize_t size, const double *data)
{
    return _createArray1(size, NPY_DOUBLE, data);
}

PyObject *createFloatArray1(Py_ssize_t size, const float *data)
{
    return _createArray1(size, NPY_FLOAT, data);
}

PyObject *createIntArray1(Py_ssize_t size, const int *data)
{
    return _createArray1(size, NPY_INT, data);
}

#else // HAVE_NUMPY

PyObject *createByteArray1(Py_ssize_t, const uint8_t *)
{
    return Py_None;
}

PyObject *createDoubleArray1(Py_ssize_t, const double *)
{
    return Py_None;
}

PyObject *createFloatArray1(Py_ssize_t, const float *)
{
    return Py_None;
}

PyObject *createIntArray1(Py_ssize_t, const int *)
{
    return Py_None;
}

#endif // !HAVE_NUMPY

} //namespace Shiboken::Numpy
