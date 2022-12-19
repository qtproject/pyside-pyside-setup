// Copyright (C) 2016 The Qt Company Ltd.
// Copyright (C) 2013 Kitware, Inc.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef TRANSFORM_H
#define TRANSFORM_H

#include "point.h"

#include "libsamplemacros.h"

LIBSAMPLE_API Point applyHomogeneousTransform(const Point &in,
                                              double m11, double m12, double m13,
                                              double m21, double m22, double m23,
                                              double m31, double m32, double m33,
                                              bool *okay);

#endif // TRANSFORM_H
