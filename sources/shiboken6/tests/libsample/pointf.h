// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef POINTF_H
#define POINTF_H

#include "libsamplemacros.h"
#include "point.h"

#include <utility>

class LIBSAMPLE_API PointF
{
public:
    PointF(const Point &point);
    PointF(double x = 0.0, double y = 0.0);
    ~PointF() {}

    inline double x() const { return m_x; }
    inline double y() const { return m_y; }

    inline void setX(double x) { m_x = x; }
    inline void setY(double y) { m_y = y; }

    // This method could simply return the midpoint,
    // but the interesting part of the test is to set the
    // result in the pointer argument.
    void midpoint(const PointF &other, PointF *midpoint) const;

    // The != operator is not implemented for the purpose of testing
    // for the absence of the __ne__ method in the Python binding.
    bool operator==(const PointF &other);

    PointF operator+(const PointF &other);
    PointF operator-(const PointF &other);

    friend LIBSAMPLE_API PointF operator*(const PointF &pt, double mult);
    friend LIBSAMPLE_API PointF operator*(const PointF &pt, int mult);
    friend LIBSAMPLE_API PointF operator*(double mult, const PointF &pt);
    friend LIBSAMPLE_API PointF operator*(int mult, const PointF &pt);
    friend LIBSAMPLE_API PointF operator-(const PointF &pt);
    friend LIBSAMPLE_API bool operator!(const PointF &pt);

    PointF &operator+=(PointF &other);
    PointF &operator-=(PointF &other);

    void show() const;

private:
    double m_x;
    double m_y;
};

LIBSAMPLE_API PointF operator*(const PointF &pt, double mult);
LIBSAMPLE_API PointF operator*(const PointF &pt, int mult);
LIBSAMPLE_API PointF operator*(double mult, const PointF &pt);
LIBSAMPLE_API PointF operator*(int mult, const PointF &pt);
LIBSAMPLE_API PointF operator-(const PointF &pt);
LIBSAMPLE_API bool operator!(const PointF &pt);

LIBSAMPLE_API PointF operator*(const PointF &pt, double multiplier);

#endif // POINTF_H
