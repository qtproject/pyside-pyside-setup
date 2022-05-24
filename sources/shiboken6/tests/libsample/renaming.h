// Copyright (C) 2019 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef RENAMING_H
#define RENAMING_H

#include "libsamplemacros.h"

class LIBSAMPLE_API ToBeRenamedValue
{
public:
    int value() const;
    void setValue(int v);

private:
    int m_value = 42;
};

class LIBSAMPLE_API RenamedUser
{
public:
    void useRenamedValue(const ToBeRenamedValue &v);
};

#endif // POINT_H
