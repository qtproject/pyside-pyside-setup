// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#include "ctparam.h"

namespace SampleNamespace
{

CtParam::CtParam(int value) : m_value(value)
{
}

CtParam::~CtParam() = default;

int CtParam::value() const
{
    return m_value;
}

} // namespace SampleNamespace
