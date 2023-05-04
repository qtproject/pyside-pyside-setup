// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

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
    case Shiboken::Numpy::View::Int16:
        return xyDataToQPointHelper<int16_t, QPointF>(xv.data, yv.data, size);
    case Shiboken::Numpy::View::Unsigned16:
        return xyDataToQPointHelper<uint16_t, QPointF>(xv.data, yv.data, size);
    case Shiboken::Numpy::View::Int:
        return xyDataToQPointHelper<int, QPointF>(xv.data, yv.data, size);
    case Shiboken::Numpy::View::Unsigned:
        return xyDataToQPointHelper<unsigned, QPointF>(xv.data, yv.data, size);
    case Shiboken::Numpy::View::Int64:
        return xyDataToQPointHelper<int64_t, QPointF>(xv.data, yv.data, size);
    case Shiboken::Numpy::View::Unsigned64:
        return xyDataToQPointHelper<uint64_t, QPointF>(xv.data, yv.data, size);
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
    case Shiboken::Numpy::View::Int16:
        return xyDataToQPointHelper<int16_t, QPoint>(xv.data, yv.data, size);
    case Shiboken::Numpy::View::Unsigned16:
        return xyDataToQPointHelper<uint16_t, QPoint>(xv.data, yv.data, size);
    case Shiboken::Numpy::View::Int:
        return xyDataToQPointHelper<int, QPoint>(xv.data, yv.data, size);
    case Shiboken::Numpy::View::Unsigned:
        return xyDataToQPointHelper<unsigned, QPoint>(xv.data, yv.data, size);
    case Shiboken::Numpy::View::Int64:
        return xyDataToQPointHelper<int64_t, QPoint>(xv.data, yv.data, size);
    case Shiboken::Numpy::View::Unsigned64:
        return xyDataToQPointHelper<uint64_t, QPoint>(xv.data, yv.data, size);
    case Shiboken::Numpy::View::Float:
        return xyFloatDataToQPointHelper<float>(xv.data, yv.data, size);
    case Shiboken::Numpy::View::Double:
        break;
    }
    return xyFloatDataToQPointHelper<double>(xv.data, yv.data, size);
}

} //namespace PySide::Numpy
