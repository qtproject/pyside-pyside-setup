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

#include "pyside_numpy.h"
#include <sbknumpyview.h>

// Convert X,Y of type T data to a list of points (QPoint, PointF)
template <class T, class Point>
static QList<Point>
    xyDataToQPointHelper(const void *xData, const void *yData, qsizetype size)
{
    auto *x = reinterpret_cast<const T *>(xData);
    auto *y = reinterpret_cast<const T *>(yData);
    QList<Point> result;
    result.reserve(size);
    for (auto xEnd = x + size; x < xEnd; ++x, ++y)
        result.append(Point(*x, *y));
    return result;
}

// Convert X,Y of double/float type data to a list of QPoint (rounding)
template <class T>
static QList<QPoint>
    xyFloatDataToQPointHelper(const void *xData, const void *yData, qsizetype size)
{
    auto *x = reinterpret_cast<const T *>(xData);
    auto *y = reinterpret_cast<const T *>(yData);
    QList<QPoint> result;
    result.reserve(size);
    for (auto xEnd = x + size; x < xEnd; ++x, ++y)
        result.append(QPoint(qRound(*x), qRound(*y)));
    return result;
}

namespace PySide::Numpy
{

QList<QPointF> xyDataToQPointFList(PyObject *pyXIn, PyObject *pyYIn)
{
    auto xv = Shiboken::Numpy::View::fromPyObject(pyXIn);
    auto yv = Shiboken::Numpy::View::fromPyObject(pyYIn);
    if (!xv.sameLayout(yv))
        return {};
    const qsizetype size = qMin(xv.dimensions[0], yv.dimensions[0]);
    if (size == 0)
        return {};
    switch (xv.type) {
    case Shiboken::Numpy::View::Int:
        return xyDataToQPointHelper<int, QPointF>(xv.data, yv.data, size);
    case Shiboken::Numpy::View::Unsigned:
        return xyDataToQPointHelper<unsigned, QPointF>(xv.data, yv.data, size);
    case Shiboken::Numpy::View::Float:
        return xyDataToQPointHelper<float, QPointF>(xv.data, yv.data, size);
    case Shiboken::Numpy::View::Double:
        break;
    }
    return xyDataToQPointHelper<double, QPointF>(xv.data, yv.data, size);
}

QList<QPoint> xyDataToQPointList(PyObject *pyXIn, PyObject *pyYIn)
{
    auto xv = Shiboken::Numpy::View::fromPyObject(pyXIn);
    auto yv = Shiboken::Numpy::View::fromPyObject(pyYIn);
    if (!xv.sameLayout(yv))
        return {};
    const qsizetype size = qMin(xv.dimensions[0], yv.dimensions[0]);
    if (size == 0)
        return {};
    switch (xv.type) {
    case Shiboken::Numpy::View::Int:
        return xyDataToQPointHelper<int, QPoint>(xv.data, yv.data, size);
    case Shiboken::Numpy::View::Unsigned:
        return xyDataToQPointHelper<unsigned, QPoint>(xv.data, yv.data, size);
    case Shiboken::Numpy::View::Float:
        return xyFloatDataToQPointHelper<float>(xv.data, yv.data, size);
    case Shiboken::Numpy::View::Double:
        break;
    }
    return xyFloatDataToQPointHelper<double>(xv.data, yv.data, size);
}

} //namespace PySide::Numpy
