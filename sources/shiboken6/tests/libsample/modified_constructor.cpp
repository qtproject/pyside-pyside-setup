// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "modified_constructor.h"

ModifiedConstructor::ModifiedConstructor(int first_arg)
{
    m_stored_value = first_arg;
}

int ModifiedConstructor::retrieveValue() const
{
    return m_stored_value;
}


