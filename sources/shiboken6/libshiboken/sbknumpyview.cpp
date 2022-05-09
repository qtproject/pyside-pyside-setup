/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of Qt for Python.
**
** $QT_BEGIN_LICENSE:LGPL$
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** GNU Lesser General Public License Usage
** Alternatively, this file may be used under the terms of the GNU Lesser
** General Public License version 3 as published by the Free Software
** Foundation and appearing in the file LICENSE.LGPL3 included in the
** packaging of this file. Please review the following information to
** ensure the GNU Lesser General Public License version 3 requirements
** will be met: https://www.gnu.org/licenses/lgpl-3.0.html.
**
** GNU General Public License Usage
** Alternatively, this file may be used under the terms of the GNU
** General Public License version 2.0 or (at your option) the GNU General
** Public license version 3 or any later version approved by the KDE Free
** Qt Foundation. The licenses are as published by the Free Software
** Foundation and appearing in the file LICENSE.GPL2 and LICENSE.GPL3
** included in the packaging of this file. Please review the following
** information to ensure the GNU General Public License requirements will
** be met: https://www.gnu.org/licenses/gpl-2.0.html and
** https://www.gnu.org/licenses/gpl-3.0.html.
**
** $QT_END_LICENSE$
**
****************************************************************************/

// included by sbknumpy.cpp

#include "helper.h"
#include <iostream>
#include <iomanip>

#ifdef HAVE_NUMPY

namespace Shiboken {
namespace Numpy {

View View::fromPyObject(PyObject *pyIn)
{
    if (pyIn == nullptr || PyArray_Check(pyIn) == 0)
        return {};
    auto *ar = reinterpret_cast<PyArrayObject *>(pyIn);
    if ((PyArray_FLAGS(ar) & NPY_ARRAY_C_CONTIGUOUS) == 0)
        return {};
    const int ndim = PyArray_NDIM(ar);
    if (ndim > 2)
        return {};

    View::Type type;
    switch (PyArray_TYPE(ar)) {
    case NPY_INT:
        type = View::Int;
        break;
    case NPY_UINT:
        type = View::Unsigned;
        break;
    case NPY_FLOAT:
        type = View::Float;
        break;
    case NPY_DOUBLE:
        type = View::Double;
        break;
    default:
        return {};
    }

    View result;
    result.ndim = ndim;
    result.type = type;
    result.data = PyArray_DATA(ar);
    result.dimensions[0] = PyArray_DIMS(ar)[0];
    result.stride[0] = PyArray_STRIDES(ar)[0];
    if (ndim > 1) {
        result.dimensions[1] = PyArray_DIMS(ar)[1];
        result.stride[1] = PyArray_STRIDES(ar)[1];
    } else {
        result.dimensions[1] = result.stride[1] = 0;
    }
    return result;
}

} // namespace Numpy

template <class T>
static void debugArray(std::ostream &str, const  T *data, int n)
{
    static const int maxData = 10;
    str << " = ";
    auto *end = data + std::min(n, maxData);
    for (auto *d = data; d != end; ++d) {
        if (d != data)
            str << ", ";
        str << *d;
    }
    if (n > maxData)
        str << "...";
}

std::ostream &operator<<(std::ostream &str, const debugPyArrayObject &a)
{
    str << "PyArrayObject(";
    if (a.m_object == nullptr) {
        str << '0';
    } else if (PyArray_Check(a.m_object) != 0) {
        auto *ar = reinterpret_cast<PyArrayObject *>(a.m_object);
        const int ndim = PyArray_NDIM(ar);
        const int type = PyArray_TYPE(ar);
        const int flags  = PyArray_FLAGS(ar);
        str << "ndim=" << ndim << " [";
        for (int d = 0; d < ndim; ++d) {
            if (d)
                str << ", ";
            str << PyArray_DIMS(ar)[d];
        }
        str << "], type=";
        switch (type) {
        case NPY_INT:
            str << "int";
            break;
        case NPY_UINT:
            str << "uint";
            break;
        case NPY_FLOAT:
            str << "float";
            break;
        case NPY_DOUBLE:
            str << "double";
            break;
        default:
            str << '(' << type << ')';
            break;
        }
        str << ", flags=0x" << std::hex << flags << std::dec;
        if ((flags & NPY_ARRAY_C_CONTIGUOUS) != 0)
            str << " [C-contiguous]";
        if ((flags & NPY_ARRAY_F_CONTIGUOUS) != 0)
            str << " [Fortran-contiguous]";
        if ((flags & NPY_ARRAY_ALIGNED) != 0)
                str << " [aligned]";
        if ((flags & NPY_ARRAY_OWNDATA) != 0)
                str << " [owndata]";
        if ((flags & NPY_ARRAY_WRITEABLE) != 0)
            str << " [writeable]";

        if (const int dim0 = PyArray_DIMS(ar)[0]) {
            auto *data = PyArray_DATA(ar);
            switch (type) {
            case NPY_INT:
                debugArray(str, reinterpret_cast<const int *>(data), dim0);
                break;
            case NPY_UINT:
                debugArray(str, reinterpret_cast<const unsigned *>(data), dim0);
                break;
            case NPY_FLOAT:
                debugArray(str, reinterpret_cast<const float *>(data), dim0);
                break;
            case NPY_DOUBLE:
                debugArray(str, reinterpret_cast<const double *>(data), dim0);
                break;
            }
        }
    } else {
        str << "Invalid";
    }
    str << ')';
    return str;
}

} //namespace Shiboken

#else // HAVE_NUMPY

namespace Shiboken::Numpy
{

View View::fromPyObject(PyObject *)
{
    return {};
}

std::ostream &operator<<(std::ostream &str, const debugPyArrayObject &)
{
    str << "Unimplemented function " <<  __FUNCTION__ << ", (numpy was not found).";
    return str;
}

} //namespace Shiboken::Numpy

#endif // !HAVE_NUMPY

namespace Shiboken::Numpy
{

bool View::sameLayout(const View &rhs) const
{
    return rhs && *this && ndim == rhs.ndim && type == rhs.type;
}

bool View::sameSize(const View &rhs) const
{
    return sameLayout(rhs)
        && dimensions[0] == rhs.dimensions[0] && dimensions[1] == rhs.dimensions[1];
}

std::ostream &operator<<(std::ostream &str, const View &v)
{
    str << "Shiboken::Numpy::View(";
    if (v) {
        str << "type=" << v.type << ", ndim=" << v.ndim << " ["
            << v.dimensions[0];
        if (v.ndim > 1)
           str << ", " << v.dimensions[1];
        str << "], stride=[" << v.stride[0];
        if (v.ndim > 1)
           str << ", " << v.stride[1];
        str << "], data=" << v.data;
    } else {
        str << "invalid";
    }
    str << ')';
    return str;
}

} //namespace Shiboken::Numpy
