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


#ifdef HAVE_NUMPY
// Include numpy first to get the proper PyArray_Check
#  include <numpy/arrayobject.h>
#  include "pyside_numpy.h"

// Convert X,Y of type T data to a list of points (QPoint, PointF)
template <class T, class Point>
static QList<Point>
    xyDataToQPointHelper(PyArrayObject *pyX, PyArrayObject *pyY,
                         qsizetype size)
{
    auto *x = reinterpret_cast<const T *>(PyArray_DATA(pyX));
    auto *y = reinterpret_cast<const T *>(PyArray_DATA(pyY));
    QList<Point> result;
    result.reserve(size);
    for (auto xEnd = x + size; x < xEnd; ++x, ++y)
        result.append(Point(*x, *y));
    return result;
}

// Convert X,Y of double/float type data to a list of QPoint (rounding)
template <class T>
static QList<QPoint>
    xyFloatDataToQPointHelper(PyArrayObject *pyX, PyArrayObject *pyY,
                              qsizetype size)
{
    auto *x = reinterpret_cast<const T *>(PyArray_DATA(pyX));
    auto *y = reinterpret_cast<const T *>(PyArray_DATA(pyY));
    QList<QPoint> result;
    result.reserve(size);
    for (auto xEnd = x + size; x < xEnd; ++x, ++y)
        result.append(QPoint(qRound(*x), qRound(*y)));
    return result;
}


namespace PySide::Numpy
{

bool init()
{
    import_array1(false);
    return true;
}

bool check(PyObject *pyIn)
{
    return PyArray_Check(pyIn);
}

struct XyCheck
{
    qsizetype size;
    int numpytype;
};

// Check whether pyXIn and pyYIn are 1 dimensional vectors of the same size.
// Return -1, -1 on failure.
static XyCheck checkXyData(PyArrayObject *pyX, PyArrayObject *pyY)
{
    XyCheck result{-1, -1};
    if (PyArray_NDIM(pyX) != 1 || (PyArray_FLAGS(pyX) & NPY_ARRAY_C_CONTIGUOUS) == 0)
        return result;
    if (PyArray_NDIM(pyY) != 1 || (PyArray_FLAGS(pyY) & NPY_ARRAY_C_CONTIGUOUS) == 0)
        return result;
    const int xType = PyArray_TYPE(pyX);
    const int yType = PyArray_TYPE(pyY);
    if (xType != yType)
        return result;
    result.numpytype = xType;
    result.size = qMin(PyArray_DIMS(pyX)[0], PyArray_DIMS(pyY)[0]);
    return result;
}

QList<QPointF> xyDataToQPointFList(PyObject *pyXIn, PyObject *pyYIn)
{
    auto *pyX = reinterpret_cast<PyArrayObject *>(pyXIn);
    auto *pyY = reinterpret_cast<PyArrayObject *>(pyYIn);
    XyCheck check = checkXyData(pyX, pyY);
    if (check.size <= 0)
        return {};
    switch (check.numpytype) {
    case NPY_INT:
        return xyDataToQPointHelper<int, QPointF>(pyX, pyY, check.size);
    case NPY_UINT:
        return xyDataToQPointHelper<unsigned, QPointF>(pyX, pyY, check.size);
    case NPY_FLOAT:
        return xyDataToQPointHelper<float, QPointF>(pyX, pyY, check.size);
    case NPY_DOUBLE:
        return xyDataToQPointHelper<double, QPointF>(pyX, pyY, check.size);
    default:
        break;
    }
    return {};
}

QList<QPoint> xyDataToQPointList(PyObject *pyXIn, PyObject *pyYIn)
{
    auto *pyX = reinterpret_cast<PyArrayObject *>(pyXIn);
    auto *pyY = reinterpret_cast<PyArrayObject *>(pyYIn);
    XyCheck check = checkXyData(pyX, pyY);
    if (check.size <= 0)
        return {};
    switch (check.numpytype) {
    case NPY_INT:
        return xyDataToQPointHelper<int, QPoint>(pyX, pyY, check.size);
    case NPY_UINT:
        return xyDataToQPointHelper<unsigned, QPoint>(pyX, pyY, check.size);
    case NPY_FLOAT:
        return xyFloatDataToQPointHelper<float>(pyX, pyY, check.size);
    case NPY_DOUBLE:
        return xyFloatDataToQPointHelper<double>(pyX, pyY, check.size);
    default:
        break;
    }

    return {};
}

} //namespace PySide::Numpy

#else // HAVE_NUMPY
#  include "pyside_numpy.h"
namespace PySide::Numpy
{

bool init()
{
    return true;
}

bool check(PyObject *)
{
    return false;
}

QList<QPointF> xyDataToQPointFList(PyObject *, PyObject *)
{
    qWarning("Unimplemented function %s, (numpy was not found).", __FUNCTION__);
    return {};
}

QList<QPoint> xyDataToQPointList(PyObject *, PyObject *)
{
    qWarning("Unimplemented function %s, (numpy was not found).", __FUNCTION__);
    return {};
}

} //namespace PySide::Numpy

#endif // !HAVE_NUMPY
