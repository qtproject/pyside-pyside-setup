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

#include "overload.h"

Overload::FunctionEnum Overload::overloaded()
{
    return Function0;
}

Overload::FunctionEnum Overload::overloaded(Size *)
{
    return Function1;
}

Overload::FunctionEnum Overload::overloaded(Point *, ParamEnum)
{
    return Function2;
}

Overload::FunctionEnum Overload::overloaded(const Point &)
{
    return Function3;
}

void Overload::differentReturnTypes(ParamEnum)
{

}

int Overload::differentReturnTypes(ParamEnum, int val)
{
    return val;
}

int Overload::intOverloads(const Point &, double)
{
    return 1; }

int Overload::intOverloads(int, int)
{
    return 2; }

int Overload::intOverloads(int, int, double)
{
    return 3;
}

Overload::FunctionEnum Overload::intDoubleOverloads(double, double) const
{
    return Function1;
}

Overload::FunctionEnum Overload::intDoubleOverloads(int, int) const
{
    return Function0;
}

void Overload::singleOverload(Point *)
{
}

Overload::FunctionEnum Overload::wrapperIntIntOverloads(const Polygon &, int, int)
{
    return Function1;
}

Overload::FunctionEnum Overload::wrapperIntIntOverloads(const Point &, int, int)
{
    return Function0;
}

Overload::FunctionEnum Overload::strBufferOverloads(const Str &, const char *, bool)
{
    return Function0;
}

Overload::FunctionEnum Overload::strBufferOverloads(unsigned char *, int)
{
    return Function1;
}

Overload::FunctionEnum Overload::drawText(const PointF &, const Str &)
{
    return Function1;
}

Overload::FunctionEnum Overload::drawText(const Point &, const Str &)
{
    return Function0;
}

Overload::FunctionEnum Overload::drawText(const RectF &, const Str &, const Echo &)
{
    return Function4;
}

Overload::FunctionEnum Overload::drawText(const RectF &, int, const Str &)
{
    return Function3;
}

Overload::FunctionEnum Overload::drawText(const Rect &, int, const Str &)
{
    return Function2;
}

Overload::FunctionEnum Overload::drawText(int, int, const Str &)
{
    return Function5;
}

Overload::FunctionEnum Overload::drawText(int, int, int, int, int, const Str &)
{
    return Function6;
}

Overload::FunctionEnum Overload::drawText2(const PointF &, const Str &)
{
    return Function1;
}

Overload::FunctionEnum Overload::drawText2(const Point &, const Str &)
{
    return Function0;
}

Overload::FunctionEnum Overload::drawText2(int, int, const Str &)
{
    return Function5;
}

Overload::FunctionEnum Overload::drawText2(const RectF &, const Str &, const Echo &)
{
    return Function4;
}

Overload::FunctionEnum Overload::drawText2(const RectF &, int, const Str &)
{
    return Function3;
}

Overload::FunctionEnum Overload::drawText2(const Rect &, int, const Str &)
{
    return Function2;
}

Overload::FunctionEnum Overload::drawText2(int, int, int, int, int, const Str &)
{
    return Function6;
}

Overload::FunctionEnum Overload::drawText3(const Str &, const Str &, const Str &)
{
    return Function0;
}

Overload::FunctionEnum Overload::drawText3(int, int, int, int, int)
{
    return Function1;
}

Overload::FunctionEnum Overload::drawText4(int, int, int)
{
    return Function0;
}

Overload::FunctionEnum Overload::drawText4(int, int, int, int, int)
{
    return Function1;
}

Overload::FunctionEnum Overload::acceptSequence()
{
    return Function0;
}

Overload::FunctionEnum Overload::acceptSequence(const Str &, ParamEnum)
{
    return Function2;
}

Overload::FunctionEnum Overload::acceptSequence(int, int)
{
    return Function1;
}

Overload::FunctionEnum Overload::acceptSequence(void *)
{
    return Function5;
}

Overload::FunctionEnum Overload::acceptSequence(const char *const[])
{
    return Function4;
}

Overload::FunctionEnum Overload::acceptSequence(const Size &)
{
    return Function3;
}
