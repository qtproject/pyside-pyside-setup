// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include "qtdatavisualization_helper.h"

#include <sbknumpyview.h>

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

    auto view = Shiboken::Numpy::View::fromPyObject(pyData);
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
    case Shiboken::Numpy::View::Int16:
        populateArray(xStart, deltaX, zStart, deltaZ, xSize, zSize, view.stride[0],
                      reinterpret_cast<const int16_t *>(view.data), result);
        break;
    case Shiboken::Numpy::View::Unsigned16:
        populateArray(xStart, deltaX, zStart, deltaZ, xSize, zSize, view.stride[0],
                      reinterpret_cast<const uint16_t *>(view.data), result);
        break;
    case Shiboken::Numpy::View::Int:
        populateArray(xStart, deltaX, zStart, deltaZ, xSize, zSize, view.stride[0],
                      reinterpret_cast<const int *>(view.data), result);
        break;
    case Shiboken::Numpy::View::Unsigned:
        populateArray(xStart, deltaX, zStart, deltaZ, xSize, zSize, view.stride[0],
                      reinterpret_cast<const unsigned *>(view.data), result);
        break;
    case Shiboken::Numpy::View::Int64:
        populateArray(xStart, deltaX, zStart, deltaZ, xSize, zSize, view.stride[0],
                      reinterpret_cast<const int64_t *>(view.data), result);
        break;
    case Shiboken::Numpy::View::Unsigned64:
        populateArray(xStart, deltaX, zStart, deltaZ, xSize, zSize, view.stride[0],
                      reinterpret_cast<const uint64_t *>(view.data), result);
        break;
    case Shiboken::Numpy::View::Float:
        populateArray(xStart, deltaX, zStart, deltaZ, xSize, zSize, view.stride[0],
                      reinterpret_cast<const float *>(view.data), result);
        break;
    case Shiboken::Numpy::View::Double:
        populateArray(xStart, deltaX, zStart, deltaZ, xSize, zSize, view.stride[0],
                      reinterpret_cast<const double *>(view.data), result);

        break;
    }
    return result;
}

} // namespace QtDataVisualizationHelper
