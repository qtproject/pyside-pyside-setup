// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

#ifndef OPTIONALTEST_H
#define OPTIONALTEST_H

#include "libsmartmacros.h"
#include "smart_integer.h"

#include <optional>

class LIB_SMART_API StdOptionalTestBench
{
public:
    StdOptionalTestBench();

    std::optional<int> optionalInt() const;
    void setOptionalInt(const std::optional<int> &i);
    void setOptionalIntValue(int i);

    std::optional<Integer> optionalInteger() const;
    void setOptionalInteger(const std::optional<Integer> &s);
    void setOptionalIntegerValue(Integer &s);

private:
    std::optional<int> m_optionalInt;
    std::optional<Integer> m_optionalInteger;
};

#endif // OPTIONALTEST_H
