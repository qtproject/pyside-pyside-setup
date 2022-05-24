// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#pragma once

#include "pysidetest_macros.h"

#include <QtCore/QObject>

namespace FlagsNamespace
{

enum Option {
    NoOptions = 0x0,
    ShowTabs = 0x1,
    ShowAll = 0x2,
    SqueezeBlank = 0x4
};
Q_DECLARE_FLAGS(Options, Option)
Q_DECLARE_OPERATORS_FOR_FLAGS(Options)

class PYSIDETEST_API ClassForEnum : public QObject
{
    Q_OBJECT
public:
    ClassForEnum(FlagsNamespace::Options opt = FlagsNamespace::Option::NoOptions);
    virtual ~ClassForEnum();
};

} // namespace FlagsNamespace
