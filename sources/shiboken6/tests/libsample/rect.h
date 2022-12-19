// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef RECT_H
#define RECT_H

#include "libsamplemacros.h"

class LIBSAMPLE_API Rect
{
public:
    Rect() = default;
    explicit Rect(int left, int top, int right, int bottom)
        : m_left(left), m_top(top), m_right(right), m_bottom(bottom) { }
    ~Rect() = default;

    inline int left() const { return m_left; }
    inline int top() const { return m_top; }
    inline int right() const { return m_right; }
    inline int bottom() const { return m_bottom; }
private:
    int m_left = 0;
    int m_top = 0;
    int m_right = -1;
    int m_bottom = -1;
};

class LIBSAMPLE_API RectF
{
public:
    RectF() = default;
    explicit RectF(int left, int top, int right, int bottom)
        : m_left(left), m_top(top), m_right(right), m_bottom(bottom) { }
    RectF(const Rect &other)
    {
        m_left = other.left();
        m_top = other.top();
        m_right = other.right();
        m_bottom = other.bottom();
    }
    ~RectF() = default;

    inline double left() const { return m_left; }
    inline double top() const { return m_top; }
    inline double right() const { return m_right; }
    inline double bottom() const { return m_bottom; }
private:
    double m_left = 0;
    double m_top = 0;
    double m_right = -1;
    double m_bottom = -1;
};

#endif // RECT_H
