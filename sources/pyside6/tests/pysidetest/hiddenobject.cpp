// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "hiddenobject.h"

void HiddenObject::callMe()
{
    m_called = true;
}

bool HiddenObject::wasCalled()
{
    return m_called;
}

QObject *getHiddenObject()
{
    return new HiddenObject();
}
