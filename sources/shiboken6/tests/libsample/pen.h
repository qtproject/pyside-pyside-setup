// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef PEN_H
#define PEN_H

#include "libsamplemacros.h"
#include "samplenamespace.h"

class LIBSAMPLE_API Color
{
public:
    Color() = default;
    Color(SampleNamespace::InValue arg);
    Color(unsigned int arg);

    bool isNull() const;

private:
    bool m_null = true;
};

class LIBSAMPLE_API Brush
{
public:
    enum Style { Solid, Cross };

    explicit Brush(const Color &c = {});

    operator bool() const;

    Style style() const;
    void setStyle(Style newStyle);

    const Color &color() const;
    void setColor(const Color &newColor);

private:
    Style m_style = Solid;
    Color m_color;
};

class LIBSAMPLE_API Pen
{
public:
    enum { EmptyCtor, EnumCtor, ColorCtor, CopyCtor };

    enum  RenderHints { None = 0, Antialiasing = 0x1, TextAntialiasing = 0x2 };

    Pen();
    Pen(SampleNamespace::Option option);
    Pen(const Color &color);
    Pen(const Pen &pen);
    Pen(Pen &&);
    Pen &operator=(const Pen &pen);
    Pen &operator=(Pen &&);

    // PYSIDE-1325, default initializer
    void drawLine(int x1, int y1, int x2, int y2, RenderHints renderHints = {});

    int ctorType();

    RenderHints getRenderHints() const;
    void setRenderHints(RenderHints h);

private:
    int m_ctor = EmptyCtor;
    RenderHints m_renderHints = None;
};

#endif
