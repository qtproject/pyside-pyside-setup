// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

#include "icecream.h"

#include <iostream>

Icecream::Icecream(const std::string &flavor) : m_flavor(flavor) {}

Icecream::~Icecream() = default;

std::string Icecream::getFlavor() const
{
    return m_flavor;
}

Icecream *Icecream::clone()
{
    return new Icecream(*this);
}

std::ostream &operator<<(std::ostream &str, const Icecream &i)
{
    str << i.getFlavor();
    return str;
}
