// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef DERIVEDUSINGCT_H
#define DERIVEDUSINGCT_H

#include "libsamplemacros.h"
#include "ctparam.h"

class LIBSAMPLE_API DerivedUsingCt : public SampleNamespace::CtParam
{
public:
    using CtParam::CtParam;

    void foo();
};
#endif // DERIVEDUSINGCT_H
