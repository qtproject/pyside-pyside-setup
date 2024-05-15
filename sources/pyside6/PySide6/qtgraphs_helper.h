// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef QTGRAPHS_HELPER_H
#define QTGRAPHS_HELPER_H

#include <sbkpython.h>

#include <QtGraphs/qsurfacedataproxy.h>
#include <QtCore/qlist.h>

namespace QtGraphsHelper {

QSurfaceDataArray surfaceDataFromNp(double x, double deltaX, double z, double deltaZ,
                                    PyObject *data);

} // namespace QtGraphsHelper

#endif // QTGRAPHS_HELPER_H
