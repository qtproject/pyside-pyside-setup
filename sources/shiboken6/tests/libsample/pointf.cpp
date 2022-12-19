// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "pointf.h"

#include <iostream>

PointF::PointF(const Point &point) : m_x(point.x()), m_y(point.y())
{
}

PointF::PointF(double x, double y) : m_x(x), m_y(y)
{
}

void PointF::midpoint(const PointF &other, PointF *midpoint) const
{
    if (!midpoint)
        return;
    midpoint->setX((m_x + other.m_x) / 2.0);
    midpoint->setY((m_y + other.m_y) / 2.0);
}

void PointF::show() const
{
    std::cout << "(x: " << m_x << ", y: " << m_y << ")";
}

bool PointF::operator==(const PointF &other)
{
    return m_x == other.m_x && m_y == other.m_y;
}

PointF PointF::operator+(const PointF &other)
{
    return PointF(m_x + other.m_x, m_y + other.m_y);
}

PointF PointF::operator-(const PointF &other)
{
    return PointF(m_x - other.m_x, m_y - other.m_y);
}

PointF &PointF::operator+=(PointF &other)
{
    m_x += other.m_x;
    m_y += other.m_y;
    return *this;
}

PointF &PointF::operator-=(PointF &other)
{
    m_x -= other.m_x;
    m_y -= other.m_y;
    return *this;
}

PointF operator*(const PointF &pt, double mult)
{
    return PointF(pt.m_x * mult, pt.m_y * mult);
}

PointF operator*(const PointF &pt, int mult)
{
    return PointF(int(pt.m_x) * mult, int(pt.m_y) * mult);
}

PointF operator*(double mult, const PointF &pt)
{
    return PointF(pt.m_x * mult, pt.m_y * mult);
}

PointF operator*(int mult, const PointF &pt)
{
    return PointF(int(pt.m_x) * mult, int(pt.m_y) * mult);
}

PointF operator-(const PointF &pt)
{
    return PointF(-pt.m_x, -pt.m_y);
}

bool operator!(const PointF &pt)
{
    return pt.m_x == 0.0 && pt.m_y == 0.0;
}
