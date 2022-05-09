/****************************************************************************
**
** Copyright (C) 2022 The Qt Company Ltd.
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
    enum Type { Int, Unsigned, Float, Double};

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
