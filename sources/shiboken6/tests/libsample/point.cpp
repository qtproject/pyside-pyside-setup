// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "point.h"

#include <iostream>

Point::Point(int x, int y) noexcept : m_x(x), m_y(y)
{
}

Point::Point(double x, double y) noexcept : m_x(x), m_y(y)
{
}

void Point::midpoint(const Point &other, Point *midpoint) const
{
    if (!midpoint)
        return;
    midpoint->setX((m_x + other.m_x) / 2.0);
    midpoint->setY((m_y + other.m_y) / 2.0);
}

Point *Point::copy() const
{
    Point *pt = new Point();
    pt->m_x = m_x;
    pt->m_y = m_y;
    return pt;
}

void Point::show() const
{
    std::cout << "(x: " << m_x << ", y: " << m_y << ")";
}

bool Point::operator==(const Point &other) const
{
    return m_x == other.m_x && m_y == other.m_y;
}

Point Point::operator+(const Point &other)
{
    return {m_x + other.m_x, m_y + other.m_y};
}

Point Point::operator-(const Point &other)
{
    return {m_x - other.m_x, m_y - other.m_y};
}

Point &Point::operator+=(Point &other)
{
    m_x += other.m_x;
    m_y += other.m_y;
    return *this;
}

Point &Point::operator-=(Point &other)
{
    m_x -= other.m_x;
    m_y -= other.m_y;
    return *this;
}

Point operator*(const Point &pt, double mult)
{
    return Point(pt.m_x * mult, pt.m_y * mult);
}

Point operator*(const Point &pt, int mult)
{
    return {int(pt.m_x) * mult, int(pt.m_y) * mult};
}

Point operator*(double mult, const Point &pt)
{
    return {pt.m_x * mult, pt.m_y * mult};
}

Point operator*(int mult, const Point &pt)
{
    return {int(pt.m_x) * mult, int(pt.m_y) * mult};
}

Point operator-(const Point &pt)
{
    return {-pt.m_x, -pt.m_y};
}

bool operator!(const Point &pt)
{
    return pt.m_x == 0.0 && pt.m_y == 0.0;
}

Point Point::operator/(int operand)
{
    return {m_x/operand, m_y/operand};
}

Complex transmutePointIntoComplex(const Point &point)
{
    Complex cpx(point.x(), point.y());
    return cpx;
}

Point transmuteComplexIntoPoint(const Complex &cpx)
{
    Point pt(cpx.real(), cpx.imag());
    return pt;
}
