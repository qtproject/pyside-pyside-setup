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

#ifndef OVERLOADSORT_H
#define OVERLOADSORT_H

#include "libsamplemacros.h"

#include <list>

class ImplicitTarget
{
public:
    ImplicitTarget(){}
};

class ImplicitBase
{
public:
    ImplicitBase(){}
    ImplicitBase(const ImplicitTarget &b);
};

inline ImplicitBase::ImplicitBase(const ImplicitTarget &)
{
}

class LIBSAMPLE_API SortedOverload
{
public:

    const char *overload(int x);
    const char *overload(double x);
    const char *overload(ImplicitBase x);
    const char *overload(ImplicitTarget x);
    const char *overload(const std::list<ImplicitBase> &x);

    int implicit_overload(const ImplicitBase &x);

    const char *overloadDeep(int x, ImplicitBase &y);

    inline const char* pyObjOverload(int, int) { return "int,int"; }
    inline const char* pyObjOverload(unsigned char*, int) { return "PyObject,int"; }

};

class LIBSAMPLE_API CustomOverloadSequence
{
public:
    int overload(short v) const;
    int overload(int v) const;
};

#endif // OVERLOADSORT_H

