// Copyright (C) 2019 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "renaming.h"

#include <iostream>

int ToBeRenamedValue::value() const
{
        return m_value;
}

void ToBeRenamedValue::setValue(int v)
{
    m_value = v;
}

void RenamedUser::useRenamedValue(const ToBeRenamedValue &v)
{
    std::cout << __FUNCTION__ << ' ' << v.value() << '\n';
}
