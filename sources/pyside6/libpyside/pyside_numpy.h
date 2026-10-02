// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// Qt-Security score:significant reason:default

#ifndef PYSIDE_NUMPY_H
#define PYSIDE_NUMPY_H

#include <sbkpython.h>
#include <sbknumpycheck.h>

#include <pysidemacros.h>

#include <QtCore/qlist.h>
#include <QtCore/qpoint.h>

namespace PySide::Numpy
{

/*!
    Creates a list of QPointF from 2 equally sized numpy arrays of x data
    \a pyXIn and y data \a pyYIn (float, double).
*/
PYSIDE_API QList<QPointF> xyDataToQPointFList(PyObject *pyXIn, PyObject *pyYIn);

/*!
    Creates a list of QPoint from 2 equally sized numpy arrays of x data
    \a pyXIn and y data \a pyYIn (int).
*/
PYSIDE_API QList<QPoint> xyDataToQPointList(PyObject *pyXIn, PyObject *pyYIn);

} //namespace PySide::Numpy

#endif // PYSIDE_NUMPY_H
