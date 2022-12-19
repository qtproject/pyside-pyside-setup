// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "virtualmethods.h"

int VirtualDtor::dtor_called = 0;

double VirtualMethods::virtualMethod0(Point pt, int val, Complex cpx, bool b)
{
    return (pt.x() * pt.y() * val) + cpx.imag() + ((int) b);
}

bool VirtualMethods::createStr(const char *text, Str *&ret)
{
    if (!text) {
        ret = nullptr;
        return false;
    }

    ret = new Str(text);
    return true;
}

void VirtualMethods::getMargins(int *left, int *top, int *right, int *bottom) const
{
    *left = m_left;
    *top = m_top;
    *right = m_right;
    *bottom = m_bottom;
}

int VirtualMethods::recursionOnModifiedVirtual(Str) const
{
    return 0;
}

const Str & VirtualMethods::returnConstRef() const
{
    static const Str result;
    return result;
}

int VirtualMethods::stringViewLength(std::string_view in) const
{
    return int(in.size());
}

double VirtualDaughter2::virtualMethod0(Point pt, int val, Complex cpx, bool b)
{
    return 42 + VirtualMethods::virtualMethod0(pt, val, cpx, b);
}

int VirtualDaughter2::sum0(int a0, int a1, int a2)
{
    return 42 + VirtualMethods::sum0(a0, a1, a2);
}

double VirtualFinalDaughter::virtualMethod0(Point pt, int val, Complex cpx, bool b)
{
    return 42 + VirtualMethods::virtualMethod0(pt, val, cpx, b);
}

int VirtualFinalDaughter::sum0(int a0, int a1, int a2)
{
    return 42 + VirtualMethods::sum0(a0, a1, a2);
}
