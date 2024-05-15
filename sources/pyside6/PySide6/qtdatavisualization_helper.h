// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef QTDATAVISUALIZATION_HELPER_H
#define QTDATAVISUALIZATION_HELPER_H

#include <sbkpython.h>

#include <QtDataVisualization/qsurfacedataproxy.h>
#include <QtCore/qlist.h>

namespace QtDataVisualizationHelper {

QSurfaceDataArray *surfaceDataFromNp(double x, double deltaX, double z, double deltaZ,
                                     PyObject *data);

} // namespace QtDataVisualizationHelper

#endif // QTDATAVISUALIZATION_HELPER_H
