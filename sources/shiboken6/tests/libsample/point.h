// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef POINT_H
#define POINT_H

#include "libsamplemacros.h"
#include "complex.h"

#include <utility>

class LIBSAMPLE_API Point
{
public:
    Point(int x = 0, int y = 0);
    Point(double x, double y);
    ~Point() = default;

    inline double x() const { return m_x; }
    inline double y() const { return m_y; }

    inline void setX(double x) { m_x = x; }
    inline void setY(double y) { m_y = y; }
    inline void setXAsUint(unsigned int x) { m_x = x; }
    inline void setYAsUint(unsigned int y) { m_y = y; }

    // This method could simply return the midpoint,
    // but the interesting part of the test is to set the
    // result in the pointer argument.
    void midpoint(const Point &other, Point *midpoint) const;

    Point *copy() const;

    inline const Point &getConstReferenceToSelf() const { return *this; }
    inline const Point *getSelf() const { return this; }

    // The != operator is not implemented for the purpose of testing
    // for the absense of the __ne__ method in the Python binding.
    bool operator==(const Point &other);

    Point operator+(const Point &other);
    Point operator-(const Point &other);
    Point operator/(int operand);

    friend LIBSAMPLE_API Point operator*(const Point &pt, double mult);
    friend LIBSAMPLE_API Point operator*(const Point &pt, int mult);
    friend LIBSAMPLE_API Point operator*(double mult, const Point &pt);
    friend LIBSAMPLE_API Point operator*(int mult, const Point &pt);
    friend LIBSAMPLE_API Point operator-(const Point &pt);
    friend LIBSAMPLE_API bool operator!(const Point &pt);

    Point &operator+=(Point &other);
    Point &operator-=(Point &other);

    void show() const;

private:
    double m_x;
    double m_y;
};

LIBSAMPLE_API Point operator*(const Point &pt, double mult);
LIBSAMPLE_API Point operator*(const Point &pt, int mult);
LIBSAMPLE_API Point operator*(double mult, const Point &pt);
LIBSAMPLE_API Point operator*(int mult, const Point &pt);
LIBSAMPLE_API Point operator-(const Point &pt);
LIBSAMPLE_API bool operator!(const Point &pt);

LIBSAMPLE_API Complex transmutePointIntoComplex(const Point &point);
LIBSAMPLE_API Point transmuteComplexIntoPoint(const Complex &cpx);

LIBSAMPLE_API Point operator*(const Point &pt, double multiplier);

#endif // POINT_H
