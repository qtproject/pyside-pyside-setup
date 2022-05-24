// Copyright (C) 2016 The Qt Company Ltd.
// Copyright (C) 2013 Kitware, Inc.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "transform.h"

#ifdef _WIN32
#include <math.h>
#include <float.h>
static inline bool isfinite(double a) { return _finite(a); }
#else
#include <cmath>
#endif

using namespace std;

Point applyHomogeneousTransform(
    const Point& in,
    double m11, double m12, double m13,
    double m21, double m22, double m23,
    double m31, double m32, double m33,
    bool* okay)
{
    double x = m11 * in.x() + m12 * in.y() + m13;
    double y = m21 * in.x() + m22 * in.y() + m23;
    double w = m31 * in.x() + m32 * in.y() + m33;

    if (isfinite(w) && fabs(w) > 1e-10)
    {
        if (okay)
            *okay = true;
        return Point(x / w, y / w);
    }
    else
    {
        if (okay)
            *okay = false;
        return Point();
    }
}
