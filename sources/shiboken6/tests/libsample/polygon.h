// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef POLYGON_H
#define POLYGON_H

#include "libsamplemacros.h"
#include "point.h"

#include <list>

class LIBSAMPLE_API Polygon
{
public:
    using PointList = std::list<Point>;

    Polygon() {}
    Polygon(double x, double y);
    Polygon(Point point);
    Polygon(PointList points);
    ~Polygon() {}

    void addPoint(Point point);

    inline const PointList &points() const { return m_points; }

    // This method intentionally receives and returns copies of a Polygon object.
    static Polygon doublePolygonScale(Polygon polygon);

    // This method invalidates the argument to be used for Polygon(Point) implicit conversion.
    static void stealOwnershipFromPython(Point *point);

    // This method invalidates the argument to be used in a call to doublePolygonScale(Polygon).
    static void stealOwnershipFromPython(Polygon *polygon);

private:
    PointList m_points;
};

#endif // POLYGON_H
