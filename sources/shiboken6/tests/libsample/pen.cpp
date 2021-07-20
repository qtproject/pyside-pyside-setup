/****************************************************************************
**
** Copyright (C) 2016 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of the test suite of Qt for Python.
**
** $QT_BEGIN_LICENSE:GPL-EXCEPT$
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** GNU General Public License Usage
** Alternatively, this file may be used under the terms of the GNU
** General Public License version 3 as published by the Free Software
** Foundation with exceptions as appearing in the file LICENSE.GPL3-EXCEPT
** included in the packaging of this file. Please review the following
** information to ensure the GNU General Public License requirements will
** be met: https://www.gnu.org/licenses/gpl-3.0.html.
**
** $QT_END_LICENSE$
**
****************************************************************************/

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
