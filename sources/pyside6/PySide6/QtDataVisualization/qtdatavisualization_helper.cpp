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

#include "qtdatavisualization_helper.h"

#include <pyside_numpy.h>

#include <QtCore/QDebug>

namespace QtDataVisualizationHelper {

template <class T>
static void populateArray(double xStart, double deltaX, double zStart, double deltaZ,
                          qsizetype xSize, qsizetype zSize, qsizetype zStrideBytes,
                          const T *data, QSurfaceDataArray *result)
{
    result->reserve(zSize);
    const qsizetype zStride = zStrideBytes / sizeof(T);
    double z = zStart;
    for (qsizetype zi = 0; zi < zSize; ++zi) {
        auto *row = new QSurfaceDataRow;
        row->reserve(xSize);
        result->append(row);

        double x = xStart;
        auto *rowDataEnd = data + xSize;
        for (auto *d = data; d < rowDataEnd; ++d) {
            row->append(QSurfaceDataItem(QVector3D(x, *d, z)));
            x += deltaX;
        }

        data += zStride;
        z += deltaZ;
    }
}

QSurfaceDataArray *surfaceDataFromNp(double xStart, double deltaX, double zStart, double deltaZ,
                                     PyObject *pyData)
{
    static const char funcName[] = "QSurfaceDataProxy.resetArrayNp";

    auto *result = new QSurfaceDataArray;

    PySide::Numpy::View view = PySide::Numpy::View::fromPyObject(pyData);
    if (!view) {
        PyErr_Format(PyExc_TypeError, "Invalid array passed to %s", funcName);
        return result;
    }
    if (view.ndim != 2) {
        PyErr_Format(PyExc_TypeError, "%s expects a 2 dimensional array (%d)", view.ndim);
        return result;
    }

    const qsizetype zSize = view.dimensions[0];
    const qsizetype xSize = view.dimensions[1];
    if (zSize  == 0 || xSize == 0)
        return result;

    switch (view.type) {
    case PySide::Numpy::View::Int:
        populateArray(xStart, deltaX, zStart, deltaZ, xSize, zSize, view.stride[0],
                      reinterpret_cast<const int *>(view.data), result);
        break;
    case PySide::Numpy::View::Unsigned:
        populateArray(xStart, deltaX, zStart, deltaZ, xSize, zSize, view.stride[0],
                      reinterpret_cast<const unsigned *>(view.data), result);
        break;
    case PySide::Numpy::View::Float:
        populateArray(xStart, deltaX, zStart, deltaZ, xSize, zSize, view.stride[0],
                      reinterpret_cast<const float *>(view.data), result);
        break;
    case PySide::Numpy::View::Double:
        populateArray(xStart, deltaX, zStart, deltaZ, xSize, zSize, view.stride[0],
                      reinterpret_cast<const double *>(view.data), result);

        break;
    }
    return result;
}

} // namespace QtDataVisualizationHelper
