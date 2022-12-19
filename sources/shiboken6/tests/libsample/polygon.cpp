// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "polygon.h"

Polygon::Polygon(double x, double y)
{
    m_points.push_back(Point(x, y));
}

Polygon::Polygon(Point point)
{
    m_points.push_back(point);
}

Polygon::Polygon(PointList points)
{
    m_points = points;
}

void Polygon::addPoint(Point point)
{
    m_points.push_back(point);
}

Polygon Polygon::doublePolygonScale(Polygon polygon)
{
    Polygon result;
    for (const auto &point : polygon.points())
        result.addPoint(point * 2.0);
    return result;
}

void Polygon::stealOwnershipFromPython(Point *point)
{
    delete point;
}

void Polygon::stealOwnershipFromPython(Polygon *polygon)
{
    delete polygon;
}
