// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "pen.h"

Color::Color(SampleNamespace::InValue) : m_null(false)
{
}

Color::Color(unsigned int) : m_null(false)
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

Pen::Pen() = default;

Pen::Pen(SampleNamespace::Option) : m_ctor(EnumCtor)
{
}

Pen::Pen(const Color &) : m_ctor(ColorCtor)
{
}

Pen::Pen(const Pen &) : m_ctor(CopyCtor)
{
}

Pen::Pen(Pen &&) = default;
Pen &Pen::operator=(const Pen &pen) = default;
Pen &Pen::operator=(Pen &&) = default;

int Pen::ctorType()
{
    return m_ctor;
}

void Pen::drawLine(int, int, int, int, RenderHints)
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
