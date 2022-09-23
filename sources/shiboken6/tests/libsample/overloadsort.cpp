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

#include "overloadsort.h"

const char *SortedOverload::overload(int)
{
    return "int";
}

const char *SortedOverload::overload(double)
{
    return "double";
}

const char *SortedOverload::overload(ImplicitBase)
{
    return "ImplicitBase";
}

const char *SortedOverload::overload(ImplicitTarget)
{
    return "ImplicitTarget";
}

const char *SortedOverload::overload(const std::list<ImplicitBase> &)
{
    return "list(ImplicitBase)";
}

int SortedOverload::implicit_overload(const ImplicitBase &)
{
    return 1;
}

const char *SortedOverload::overloadDeep(int, ImplicitBase &)
{
    return "ImplicitBase";
}

int CustomOverloadSequence::overload(short v) const
{
    return v + int(sizeof(v));
}

int CustomOverloadSequence::overload(int v) const
{
    return v + 4;
}
