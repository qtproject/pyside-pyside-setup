// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

#ifndef ICECREAM_H
#define ICECREAM_H

#include "macros.h"

#include <iosfwd>
#include <string>

class BINDINGS_API Icecream
{
public:
    explicit Icecream(const std::string &flavor);
    virtual Icecream *clone();
    virtual ~Icecream();
    virtual std::string getFlavor() const;

private:
    std::string m_flavor;
};

std::ostream &operator<<(std::ostream &str, const Icecream &i);

#endif // ICECREAM_H
