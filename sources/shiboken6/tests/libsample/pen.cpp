// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "pen.h"

Color::Color(SampleNamespace::InValue arg) : m_null(false)
{
}

Color::Color(unsigned int arg) : m_null(false)
{
}

bool Color::isNull() const
{
    return m_null;
}

Brush::Brush(const Color &c) : m_color(c)
{
}

Brush::operator bool() const
{
    return !m_color.isNull();
}

Brush::Style Brush::style() const
{
    return m_style;
}

void Brush::setStyle(Style newStyle)
{
    m_style = newStyle;
}

const Color &Brush::color() const
{
    return m_color;
}

void Brush::setColor(const Color &newColor)
{
    m_color = newColor;
}

Pen::Pen() : m_ctor(EmptyCtor)
{
}

Pen::Pen(SampleNamespace::Option option) : m_ctor(EnumCtor)
{
}

Pen::Pen(const Color& color) : m_ctor(ColorCtor)
{
}

Pen::Pen(const Pen& pen) : m_ctor(CopyCtor)
{
}

int Pen::ctorType()
{
    return m_ctor;
}

void Pen::drawLine(int x1, int y1, int x2, int y2, RenderHints renderHints)
{
}

Pen::RenderHints Pen::getRenderHints() const
{
    return m_renderHints;
}

void Pen::setRenderHints(RenderHints h)
{
    m_renderHints = h;
}
