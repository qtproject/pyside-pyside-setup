// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "obj.h"

Obj::Obj(int objId) : m_objId(objId)
{
}

Obj::~Obj() = default;

bool Obj::virtualMethod(int val)
{
    return !bool(val%2);
}

