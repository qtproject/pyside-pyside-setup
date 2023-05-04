// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef SBKNUMPYVIEW_H
#define SBKNUMPYVIEW_H

#include <sbkpython.h>
#include <shibokenmacros.h>

#include <iosfwd>

namespace Shiboken::Numpy
{

/// Check whether the object is a PyArrayObject
/// \param pyIn object
/// \return Whether it is a PyArrayObject
LIBSHIBOKEN_API bool check(PyObject *pyIn);

/// A simple view of an up to 2 dimensional, C-contiguous array of a standard
/// type. It can be passed to compilation units that do not include the
/// numpy headers.
struct LIBSHIBOKEN_API View
{
    enum Type { Int, Unsigned, Float, Double, Int16, Unsigned16, Int64, Unsigned64 };

    static View fromPyObject(PyObject *pyIn);

    operator bool() const { return ndim > 0; }

    /// Return whether rhs is of the same type and dimensionality
    bool sameLayout(const View &rhs) const;
    /// Return whether rhs is of the same type dimensionality and size
    bool sameSize(const View &rhs) const;

    int ndim = 0;
    Py_ssize_t dimensions[2];
    Py_ssize_t stride[2];
    void *data = nullptr;
    Type type = Int;
};

LIBSHIBOKEN_API std::ostream &operator<<(std::ostream &, const View &v);

} //namespace Shiboken::Numpy

#endif // SBKNUMPYVIEW_H
