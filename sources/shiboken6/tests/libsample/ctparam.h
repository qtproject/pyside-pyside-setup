// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef CTPARAM_H
#define CTPARAM_H

#include "libsamplemacros.h"

namespace SampleNamespace
{

class LIBSAMPLE_API CtParam
{
public:
    explicit CtParam(int value);
    virtual ~CtParam();

    int value() const;

private:
    int m_value;
};

} // namespace SampleNamespace

#endif // CTPARAM_H
